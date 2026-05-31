import json
from pathlib import Path
from typing import List, Dict

from datetime import datetime

class IngestionTracker:
    def __init__(self):
        self.tracker_file = Path("./data/ingested_files.json")
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        self.ingested: List[Dict[str, str]] = self._load_tracker()

    def _load_tracker(self) -> List[Dict[str, str]]:
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_tracker(self):
        with open(self.tracker_file, 'w') as f:
            json.dump(self.ingested, f, indent=4)
    
    def is_ingested(self, file_path: str) -> bool:
        return any(file["file_path"] == file_path for file in self.ingested)

    def mark_as_ingested(self, file_path: str):
        # removing the extension from the file name for better readability in the tracker
        file_name = Path(file_path).stem
        self.ingested.append({
            "file_name": file_name,
            "file_path": str(file_path),
            "ingested_at": datetime.now().isoformat()
        })
        self._save_tracker()
    
    def get_new_files(self, directory: str) -> List[Path]:
        """Return list of new files not yet ingested"""
        dir_path = Path(directory)
        new_files = []
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and not self.is_ingested(str(file_path)):
                new_files.append(file_path)
        
        return new_files
    
    def get_loaded_files(self) -> List[str]:
        """Return list of ingested files with their metadata"""
        files = [file["file_name"] for file in self.ingested]
        return files
