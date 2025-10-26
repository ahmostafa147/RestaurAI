#Uses local JSON for now, might convert to Supabase or Chroma later
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import os
import sys

# Handle imports with proper path resolution
try:
    from ..models.review import Review
    from ..models.snapshot import Snapshot
except ImportError:
    # Fallback for when running from different directories
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from models.review import Review
    from models.snapshot import Snapshot

# Import Status enum with fallback to avoid scraper dependencies
try:
    from ..scrapers.pull_dataset import Status
except ImportError:
    # Define Status enum locally to avoid scraper dependencies
    from enum import Enum
    class Status(Enum):
        READY = 'ready'
        RUNNING = 'running'
        FAILED = 'failed'

from .utils import FileHandler
class DatabaseHandler:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._ensure_database_structure()
    
    def _ensure_database_structure(self) -> None:
        """Ensure the database has the proper structure"""
        data = FileHandler.read_file(self.database_path)
        if not data:
            # Initialize with empty structure
            FileHandler.write_file(self.database_path, {
                'reviews': [],
                'snapshots': []
            })
        elif isinstance(data, list):
            # Migrate old format to new format
            FileHandler.write_file(self.database_path, {
                'reviews': data,
                'snapshots': []
            })
    
    def _get_database_data(self) -> Dict[str, Any]:
        """Get the full database structure"""
        data = FileHandler.read_file(self.database_path)
        if not data:
            return {'reviews': [], 'snapshots': []}
        return data
    
    def _save_database_data(self, data: Dict[str, Any]) -> None:
        """Save the full database structure"""
        FileHandler.write_file(self.database_path, data)
    
    # Review methods
    def save_reviews(self, reviews: List[Review], overwrite: bool = False) -> None:
        data = self._get_database_data()
        #Check if the review id already exists, if it does, remove the old version.
        for r in reviews:
            for dr in data['reviews']:
                if dr['review_id'] == r.review_id:
                    data['reviews'].remove(dr)
                    break
            data['reviews'].append(r.to_dict())
        self._save_database_data(data)
    
    def get_reviews(self, review_id: int) -> Review:
        data = self._get_database_data()
        return Review.from_dict(data['reviews'][review_id])
    
    def get_all_reviews(self) -> List[Review]:
        data = self._get_database_data()
        return [Review.from_dict(review) for review in data['reviews']]
    
    def delete_review(self, review_id: str) -> None:
        data = self._get_database_data()
        data['reviews'] = [review for review in data['reviews'] if review['review_id'] != review_id]
        self._save_database_data(data)
    
    # Make snapshots save just the snapshots itself and the status
    def save_snapshot(self, snapshot: Union[Snapshot, dict, str]) -> None:
        """Save or update snapshot metadata"""
        if isinstance(snapshot, str):
            snapshot = Snapshot(snapshot, "unknown", Status.READY.value)
        elif isinstance(snapshot, dict):
            snapshot = Snapshot.from_dict(snapshot)
        elif isinstance(snapshot, Snapshot):
            pass
        else:
            raise ValueError(f"Invalid snapshot type: {type(snapshot)}")
        data = self._get_database_data()
        
        if isinstance(snapshot.status, Status):
            snapshot.status = snapshot.status.value
        # If snapshot already exists, override (they are unique)
        existing_index = None
        for i, ss in enumerate(data['snapshots']):
            if ss['snapshot_id'] == snapshot.snapshot_id:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing snapshot
            data['snapshots'][existing_index] = snapshot.to_dict()
        else:
            # Add new snapshot
            data['snapshots'].append(snapshot.to_dict())
        
        self._save_database_data(data)
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get metadata for a specific snapshot"""
        data = self._get_database_data()
        for snapshot in data['snapshots']:
            if snapshot['snapshot_id'] == snapshot_id:
                return Snapshot.from_dict(snapshot)
        return None
    
    def get_all_snapshots(self) -> List[Snapshot]:
        """Get all snapshot metadata"""
        data = self._get_database_data()
        return [Snapshot.from_dict(snapshot) for snapshot in data['snapshots']]

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete snapshot metadata"""
        data = self._get_database_data()
        data['snapshots'] = [snapshot for snapshot in data['snapshots'] 
                           if snapshot['snapshot_id'] != snapshot_id]
        self._save_database_data(data)
    
    def get_unprocessed_reviews(self) -> List[Review]:
        """Get all reviews that haven't been processed by LLM"""
        all_reviews = self.get_all_reviews()
        return [r for r in all_reviews if not getattr(r, 'llm_processed', False)]
    
    def get_reviews_by_restaurant(self, restaurant_id: str) -> List[Review]:
        """Get all reviews for a specific restaurant"""
        all_reviews = self.get_all_reviews()
        return [r for r in all_reviews if getattr(r, 'restaurant_id', None) == restaurant_id]
    
    def get_snapshots_by_restaurant(self, restaurant_id: str) -> List[Snapshot]:
        """Get all snapshots for a specific restaurant"""
        all_snapshots = self.get_all_snapshots()
        return [s for s in all_snapshots if getattr(s, 'restaurant_id', None) == restaurant_id]
    