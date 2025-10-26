import requests
from enum import Enum
from typing import Dict, Any, Union
import json
import os
import sys

# Handle imports with proper path resolution
try:
    from .env_config import token
except ImportError:
    # Fallback for when running from different directories
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from env_config import token

try:
    from src.models.snapshot import Snapshot
except ImportError:
    # Fallback when running from scrapers directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from src.models.snapshot import Snapshot

class Status(Enum):
    READY = 'ready'
    RUNNING = 'running'
    FAILED = 'failed'

class PullDataset:
    def pull_dataset(self, snapshot_id: str):
        url = f'https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}'
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"Pulled dataset for {snapshot_id}: {PullDataset.parse_ndjson(response.content)}")
        return PullDataset.parse_ndjson(response.content)
    def check_snapshot_status(self, snapshot_id: Union[str, Snapshot, dict]) -> Status:
        if isinstance(snapshot_id, Snapshot):
            snapshot_id = snapshot_id.snapshot_id
        elif isinstance(snapshot_id, dict):
            snapshot_id = snapshot_id['snapshot_id']
        elif isinstance(snapshot_id, str):
            pass
        else:
            raise ValueError(f"Invalid snapshot ID type: {type(snapshot_id)}")
        url = f'https://api.brightdata.com/datasets/v3/progress/{snapshot_id}'
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        result = response.json()
        print(f"Status response for {snapshot_id}: {result['status']}")
        if result['status'] == Status.READY.value:
            return Status.READY
        elif result['status'] == Status.RUNNING.value:
            return Status.RUNNING
        elif result['status'] == Status.FAILED.value:
            return Status.FAILED
    def safe_pull_dataset(self, snapshot_id: Union[str, Snapshot, dict]) -> Dict[str, Any]:
        if isinstance(snapshot_id, Snapshot):
            snapshot_id = snapshot_id.snapshot_id
        elif isinstance(snapshot_id, dict):
            snapshot_id = snapshot_id['snapshot_id']
        elif isinstance(snapshot_id, str):
            pass
        else:
            raise ValueError(f"Invalid snapshot ID type: {type(snapshot_id)}")
        if self.check_snapshot_status(snapshot_id) != Status.READY:
            return {}
        return self.pull_dataset(snapshot_id)
    
    @staticmethod
    def parse_ndjson(content):
        """Parse newline-delimited JSON"""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        results = []
        for line in content.strip().split('\n'):
            if line.strip():  # Skip empty lines
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Failed to parse line: {e}")
                    print(f"Line content: {line[:100]}...")  # Show first 100 chars
        
        return results 