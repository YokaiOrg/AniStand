from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME', 'anistand')
            
            self.client = AsyncIOMotorClient(mongo_url)
            self.database = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Anime collection indexes
            await self.database.anime.create_index("mal_id", unique=True)
            await self.database.anime.create_index([("title", "text"), ("title_english", "text"), ("synopsis", "text")])
            await self.database.anime.create_index("genres")
            await self.database.anime.create_index("status")
            await self.database.anime.create_index("year")
            await self.database.anime.create_index("score")
            await self.database.anime.create_index("view_count")
            
            # Comments collection indexes
            await self.database.comments.create_index("anime_id")
            await self.database.comments.create_index("created_at")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    # Anime operations
    async def create_anime(self, anime_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new anime record"""
        try:
            result = await self.database.anime.insert_one(anime_data)
            created_anime = await self.database.anime.find_one({"_id": result.inserted_id})
            return created_anime
        except Exception as e:
            logger.error(f"Error creating anime: {str(e)}")
            raise
    
    async def get_anime_by_id(self, anime_id: str) -> Optional[Dict[str, Any]]:
        """Get anime by ID"""
        try:
            anime = await self.database.anime.find_one({"id": anime_id})
            return anime
        except Exception as e:
            logger.error(f"Error getting anime by ID {anime_id}: {str(e)}")
            return None
    
    async def get_anime_by_mal_id(self, mal_id: int) -> Optional[Dict[str, Any]]:
        """Get anime by MAL ID"""
        try:
            anime = await self.database.anime.find_one({"mal_id": mal_id})
            return anime
        except Exception as e:
            logger.error(f"Error getting anime by MAL ID {mal_id}: {str(e)}")
            return None
    
    async def update_anime(self, anime_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update anime record"""
        try:
            result = await self.database.anime.update_one(
                {"id": anime_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return await self.get_anime_by_id(anime_id)
            return None
        except Exception as e:
            logger.error(f"Error updating anime {anime_id}: {str(e)}")
            return None
    
    async def search_anime(
        self, 
        query: str = None, 
        genres: List[str] = None,
        status: str = None,
        year: int = None,
        type: str = None,
        score_min: float = None,
        score_max: float = None,
        sort_by: str = "score",
        sort_order: int = -1,
        limit: int = 20,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Search anime with filters"""
        try:
            filter_query = {}
            
            # Text search
            if query:
                filter_query["$text"] = {"$search": query}
            
            # Genre filter
            if genres:
                filter_query["genres"] = {"$in": genres}
            
            # Status filter
            if status:
                filter_query["status"] = status
            
            # Year filter
            if year:
                filter_query["year"] = year
            
            # Type filter
            if type:
                filter_query["type"] = type
            
            # Score range filter
            if score_min is not None or score_max is not None:
                score_filter = {}
                if score_min is not None:
                    score_filter["$gte"] = score_min
                if score_max is not None:
                    score_filter["$lte"] = score_max
                filter_query["score"] = score_filter
            
            # Execute query
            cursor = self.database.anime.find(filter_query)
            cursor = cursor.sort(sort_by, sort_order).skip(skip).limit(limit)
            
            results = await cursor.to_list(length=limit)
            return results
            
        except Exception as e:
            logger.error(f"Error searching anime: {str(e)}")
            return []
    
    async def get_popular_anime(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular anime based on view count and score"""
        try:
            cursor = self.database.anime.find({}).sort([("view_count", -1), ("score", -1)]).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Error getting popular anime: {str(e)}")
            return []
    
    async def get_trending_anime(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending anime based on recent view activity"""
        try:
            # For now, use a combination of score and view count
            # In a real implementation, you might track daily/weekly views
            cursor = self.database.anime.find({}).sort([("score", -1), ("view_count", -1)]).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Error getting trending anime: {str(e)}")
            return []
    
    async def get_new_releases(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get new anime releases"""
        try:
            cursor = self.database.anime.find({}).sort("created_at", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Error getting new releases: {str(e)}")
            return []
    
    async def increment_view_count(self, anime_id: str) -> bool:
        """Increment view count for an anime"""
        try:
            result = await self.database.anime.update_one(
                {"id": anime_id},
                {"$inc": {"view_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error incrementing view count for {anime_id}: {str(e)}")
            return False
    
    # Comment operations
    async def create_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new comment"""
        try:
            result = await self.database.comments.insert_one(comment_data)
            created_comment = await self.database.comments.find_one({"_id": result.inserted_id})
            return created_comment
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            raise
    
    async def get_comments_by_anime(self, anime_id: str, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """Get comments for an anime"""
        try:
            cursor = self.database.comments.find({"anime_id": anime_id})
            cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Error getting comments for anime {anime_id}: {str(e)}")
            return []
    
    async def increment_comment_likes(self, comment_id: str) -> bool:
        """Increment likes for a comment"""
        try:
            result = await self.database.comments.update_one(
                {"id": comment_id},
                {"$inc": {"likes": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error incrementing likes for comment {comment_id}: {str(e)}")
            return False

# Global database manager instance
db_manager = MongoDBManager()