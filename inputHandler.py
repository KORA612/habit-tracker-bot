import os
from typing import Dict, Any
from datetime import datetime
from openai import OpenAI
from dataclasses import dataclass


@dataclass
class ProcessedActivity:
    """Data class for processed activity information"""
    time: str
    activity: str
    sentiment: str = "neutral"
    duration: int = 0  # in minutes


class InputHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        self.system_prompt = """You are an AI assistant specialized in processing daily activity logs. 
Your task is to extract structured information about activities from natural language input.

For each activity mentioned, identify:
1. The time it occurred (in HH:MM format)
2. The activity description
3. Any mentioned duration
4. The sentiment/mood (if mentioned)

Format your response as a JSON array with objects containing:
{
    "time": "HH:MM",
    "activity": "description",
    "duration": minutes_as_integer,
    "sentiment": "positive/neutral/negative"
}

Example input: "I woke up at 6:30, had a great breakfast until 7:15, then read for 45 minutes"

Example response:
[
    {"time": "06:30", "activity": "wake up", "duration": 0, "sentiment": "neutral"},
    {"time": "06:30", "activity": "breakfast", "duration": 45, "sentiment": "positive"},
    {"time": "07:15", "activity": "reading", "duration": 45, "sentiment": "neutral"}
]

Important rules:
- Always use 24-hour time format
- If duration isn't mentioned, set it to 0
- If sentiment isn't clear, use "neutral"
- Keep activity descriptions concise but clear
- Infer end times when possible
- Include all mentioned activities"""

    async def transcribe_audio(self, file_path: str) -> str:
        """Transcribe audio file to text"""
        try:
            with open(file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                )
            return transcript.text
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")

    async def process_message(self, text: str) -> list[ProcessedActivity]:
        """Process text message and extract structured activity data"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Parse the JSON response into ProcessedActivity objects
            activities_data = eval(response.choices[0].message.content)
            activities = [
                ProcessedActivity(
                    time=activity["time"],
                    activity=activity["activity"],
                    sentiment=activity["sentiment"],
                    duration=activity["duration"]
                )
                for activity in activities_data
            ]

            return activities

        except Exception as e:
            raise Exception(f"Error processing message: {str(e)}")

    async def handle_voice_message(self, file_path: str) -> list[ProcessedActivity]:
        """Handle voice message from start to finish"""
        try:
            # First transcribe
            transcript = await self.transcribe_audio(file_path)

            # Then process
            activities = await self.process_message(transcript)

            return activities

        except Exception as e:
            raise Exception(f"Error handling voice message: {str(e)}")

    def format_activities_for_display(self, activities: list[ProcessedActivity]) -> str:
        """Format processed activities into a readable message"""
        if not activities:
            return "No activities found in the message."

        message = "📋 Here's your activity log:\n\n"

        for activity in activities:
            # Add emoji based on sentiment
            sentiment_emoji = {
                "positive": "😊",
                "neutral": "😐",
                "negative": "😕"
            }.get(activity.sentiment, "😐")

            # Format duration if present
            duration_text = f" ({activity.duration} mins)" if activity.duration > 0 else ""

            message += f"⏰ {activity.time} - {activity.activity}{duration_text} {sentiment_emoji}\n"

        return message


# Usage example:
'''
handler = InputHandler()

# For voice messages:
activities = await handler.handle_voice_message("path_to_audio.ogg")

# For text messages:
activities = await handler.process_message("I woke up at 6:30 and had a great breakfast")

# Format for display:
formatted_message = handler.format_activities_for_display(activities)
'''
