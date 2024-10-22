from typing import List, Dict, Optional, Any
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import os
from dotenv import load_dotenv

class DatabaseHandler:
    def __init__(self):
        load_dotenv()
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db: Database = self.client.habit_tracker
        
        # Initialize collections
        self.users: Collection = self.db.users
        self.activities: Collection = self.db.activities
        self.habits: Collection = self.db.habits
        
        # Create indexes
        self._setup_indexes()
    
    def _setup_indexes(self) -> None:
        """Setup necessary indexes for better query performance"""
        # User indexes
        self.users.create_index([("telegram_id", pymongo.ASCENDING)], unique=True)
        
        # Activity indexes
        self.activities.create_index([
            ("user_id", pymongo.ASCENDING),
            ("timestamp", pymongo.DESCENDING)
        ])
        
        # Habit indexes
        self.habits.create_index([
            ("user_id", pymongo.ASCENDING),
            ("name", pymongo.ASCENDING)
        ])

    async def create_user(self, telegram_id: int, username: str) -> Dict[str, Any]:
        """Create a new user or get existing user"""
        user = {
            "telegram_id": telegram_id,
            "username": username,
            "created_at": datetime.utcnow(),
            "settings": {
                "timezone": "UTC",
                "daily_reminder": False,
                "reminder_time": "09:00"
            },
            "stats": {
                "total_activities": 0,
                "total_duration": 0,
                "streak": 0,
                "last_activity": None
            }
        }
        
        try:
            return self.users.find_one_and_update(
                {"telegram_id": telegram_id},
                {"$setOnInsert": user},
                upsert=True,
                return_document=pymongo.ReturnDocument.AFTER
            )
        except Exception as e:
            raise Exception(f"Error creating/updating user: {str(e)}")

    async def log_activity(self, 
                          user_id: int, 
                          activity: str, 
                          timestamp: str, 
                          duration: int = 0,
                          sentiment: str = "neutral") -> Dict[str, Any]:
        """Log a new activity for a user"""
        activity_doc = {
            "user_id": user_id,
            "activity": activity,
            "timestamp": timestamp,
            "duration": duration,
            "sentiment": sentiment,
            "created_at": datetime.utcnow()
        }
        
        try:
            # Insert activity
            result = self.activities.insert_one(activity_doc)
            
            # Update user stats
            self.users.update_one(
                {"telegram_id": user_id},
                {
                    "$inc": {
                        "stats.total_activities": 1,
                        "stats.total_duration": duration
                    },
                    "$set": {
                        "stats.last_activity": datetime.utcnow()
                    }
                }
            )
            
            # Check and update streak
            self._update_streak(user_id)
            
            return activity_doc
            
        except Exception as e:
            raise Exception(f"Error logging activity: {str(e)}")

    async def get_user_activities(self, 
                                user_id: int, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                limit: int = 10) -> List[Dict[str, Any]]:
        """Get user activities within a date range"""
        query = {"user_id": user_id}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        try:
            return list(self.activities
                       .find(query)
                       .sort("timestamp", pymongo.DESCENDING)
                       .limit(limit))
        except Exception as e:
            raise Exception(f"Error retrieving activities: {str(e)}")

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            user = self.users.find_one({"telegram_id": user_id})
            if not user:
                raise Exception("User not found")
            return user.get("stats", {})
        except Exception as e:
            raise Exception(f"Error retrieving user stats: {str(e)}")

    def _update_streak(self, user_id: int) -> None:
        """Update user's activity streak"""
        try:
            user = self.users.find_one({"telegram_id": user_id})
            if not user:
                return

            last_activity = user["stats"]["last_activity"]
            current_time = datetime.utcnow()
            
            # If last activity was within 24 hours, increment streak
            if (last_activity and 
                (current_time - last_activity).days <= 1):
                self.users.update_one(
                    {"telegram_id": user_id},
                    {"$inc": {"stats.streak": 1}}
                )
            else:
                # Reset streak
                self.users.update_one(
                    {"telegram_id": user_id},
                    {"$set": {"stats.streak": 1}}
                )
                
        except Exception as e:
            print(f"Error updating streak: {str(e)}")

    async def add_or_update_habit(self, 
                                user_id: int, 
                                habit_name: str,
                                target_frequency: str = "daily",
                                target_duration: int = 0) -> Dict[str, Any]:
        """Add or update a habit tracking goal"""
        habit = {
            "user_id": user_id,
            "name": habit_name,
            "target_frequency": target_frequency,
            "target_duration": target_duration,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "streak": 0,
            "total_completions": 0
        }
        
        try:
            return self.habits.find_one_and_update(
                {"user_id": user_id, "name": habit_name},
                {"$set": habit},
                upsert=True,
                return_document=pymongo.ReturnDocument.AFTER
            )
        except Exception as e:
            raise Exception(f"Error adding/updating habit: {str(e)}")

# Example usage:
"""
db = DatabaseHandler()

# Create/get user
user = await db.create_user(telegram_id=123456, username="john_doe")

# Log activity
activity = await db.log_activity(
    user_id=123456,
    activity="reading",
    timestamp="2024-01-01 14:30",
    duration=30,
    sentiment="positive"
)

# Get user activities
activities = await db.get_user_activities(user_id=123456, limit=5)

# Get user stats
stats = await db.get_user_stats(user_id=123456)

# Add habit tracking
habit = await db.add_or_update_habit(
    user_id=123456,
    habit_name="reading",
    target_frequency="daily",
    target_duration=30
)
"""