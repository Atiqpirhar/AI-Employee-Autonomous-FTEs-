#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filesystem Watcher - Monitors a drop folder for new files.

This watcher monitors a designated "drop folder" for new files. When a file
is added, it creates an action file in the Needs_Action folder for Claude
Code to process.

This is the simplest watcher to set up and is perfect for the Bronze tier.

Usage:
    python filesystem_watcher.py [vault_path] [drop_folder_path]
    
Example:
    python filesystem_watcher.py ./AI_Employee_Vault ./drop_folder
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from base_watcher import BaseWatcher


class FilesystemWatcher(BaseWatcher):
    """
    Watches a folder for new files and creates action files.
    
    Use cases:
    - Drop invoices for processing
    - Add documents for summarization
    - Submit forms for data extraction
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, 
                 check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            drop_folder: Path to the folder to monitor (default: vault/Drop_Folder)
            check_interval: How often to check for new files (in seconds)
        """
        super().__init__(vault_path, check_interval)
        
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Drop_Folder'
        
        # Create drop folder if it doesn't exist
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by their hash
        self.processed_files: Dict[str, str] = {}  # hash -> filename
        self._load_processed_files()
        
        self.logger.info(f"Drop folder: {self.drop_folder.absolute()}")
    
    def _load_processed_files(self):
        """Load the list of already processed files from a tracking file."""
        tracking_file = self.vault_path / '.processed_files.txt'
        if tracking_file.exists():
            try:
                for line in tracking_file.read_text().splitlines():
                    if '|' in line:
                        file_hash, filename = line.split('|', 1)
                        self.processed_files[file_hash] = filename
                self.logger.info(f"Loaded {len(self.processed_files)} processed file records")
            except Exception as e:
                self.logger.warning(f"Could not load processed files: {e}")
    
    def _save_processed_file(self, file_hash: str, filename: str):
        """Save a processed file record to the tracking file."""
        tracking_file = self.vault_path / '.processed_files.txt'
        with open(tracking_file, 'a') as f:
            f.write(f"{file_hash}|{filename}\n")
        self.processed_files[file_hash] = filename
    
    def _calculate_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file for deduplication."""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def check_for_updates(self) -> List[Path]:
        """
        Check the drop folder for new files.
        
        Returns:
            List of new file paths that haven't been processed
        """
        new_files = []
        
        try:
            for filepath in self.drop_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_hash = self._calculate_hash(filepath)
                    
                    if file_hash not in self.processed_files:
                        self.logger.debug(f"New file detected: {filepath.name}")
                        new_files.append(filepath)
        except Exception as e:
            self.logger.error(f"Error scanning drop folder: {e}")
        
        return new_files
    
    def create_action_file(self, filepath: Path) -> Optional[Path]:
        """
        Create an action file for a dropped file.
        
        Copies the file to the vault and creates a markdown action file
        with metadata about the dropped file.
        
        Args:
            filepath: Path to the new file in the drop folder
            
        Returns:
            Path to the created action file
        """
        try:
            # Calculate file info
            file_hash = self._calculate_hash(filepath)
            file_size = filepath.stat().st_size
            file_ext = filepath.suffix.lower()
            
            # Determine file type category
            type_category = self._categorize_file(file_ext)
            
            # Copy file to vault for safekeeping
            files_folder = self.vault_path / 'Files'
            files_folder.mkdir(parents=True, exist_ok=True)
            dest_path = files_folder / filepath.name
            
            # Handle duplicate filenames
            counter = 1
            while dest_path.exists():
                stem = filepath.stem
                dest_path = files_folder / f"{stem}_{counter}{filepath.suffix}"
                counter += 1
            
            shutil.copy2(filepath, dest_path)
            
            # Create action file content
            content = self._create_action_content(
                original_name=filepath.name,
                copied_path=dest_path,
                file_size=file_size,
                file_type=type_category,
                file_hash=file_hash
            )
            
            # Generate filename and write action file
            filename = self._generate_filename('FILE', filepath.stem)
            action_file = self._write_action_file(filename, content)
            
            # Mark as processed
            self._save_processed_file(file_hash, filepath.name)
            
            # Optionally remove from drop folder after processing
            # (comment out if you want to keep originals)
            # filepath.unlink()
            
            self.logger.info(f"Processed file: {filepath.name} -> {dest_path.name}")
            
            return action_file
            
        except Exception as e:
            self.logger.error(f"Error processing file {filepath.name}: {e}")
            return None
    
    def _categorize_file(self, extension: str) -> str:
        """Categorize file by extension for processing hints."""
        categories = {
            '.pdf': 'document',
            '.doc': 'document',
            '.docx': 'document',
            '.txt': 'text',
            '.md': 'markdown',
            '.csv': 'data',
            '.xls': 'spreadsheet',
            '.xlsx': 'spreadsheet',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.zip': 'archive',
            '.rar': 'archive',
        }
        return categories.get(extension, 'unknown')
    
    def _create_action_content(self, original_name: str, copied_path: Path,
                               file_size: int, file_type: str, 
                               file_hash: str) -> str:
        """Create the markdown content for the action file."""
        
        # Generate suggested actions based on file type
        suggested_actions = self._get_suggested_actions(file_type)
        
        content = f"""---
type: file_drop
original_name: {original_name}
copied_path: {copied_path.as_posix()}
file_size: {file_size} bytes
file_type: {file_type}
file_hash: {file_hash}
received: {datetime.now().isoformat()}
priority: normal
status: pending
---

# File Drop for Processing

A new file was dropped into the monitored folder.

## File Details

| Property | Value |
|----------|-------|
| Original Name | `{original_name}` |
| Stored Path | `{copied_path.as_posix()}` |
| Size | {file_size:,} bytes ({file_size / 1024:.2f} KB) |
| Type | {file_type} |

## Content Preview

<!-- AI Employee: Read the file and provide a summary here -->

---

## Suggested Actions

{chr(10).join(f'- [ ] {action}' for action in suggested_actions)}

---

*File processed by Filesystem Watcher v0.1*
"""
        return content
    
    def _get_suggested_actions(self, file_type: str) -> List[str]:
        """Get suggested actions based on file type."""
        actions = {
            'document': [
                'Read and summarize the document',
                'Extract key information',
                'File in appropriate category',
                'Take any required actions'
            ],
            'text': [
                'Read and process the content',
                'Extract any action items',
                'Archive after processing'
            ],
            'markdown': [
                'Review markdown content',
                'Merge with existing notes if applicable',
                'Archive after processing'
            ],
            'data': [
                'Analyze the data',
                'Extract insights or summaries',
                'Update relevant records'
            ],
            'spreadsheet': [
                'Review spreadsheet contents',
                'Extract key data points',
                'Update accounting or tracking sheets'
            ],
            'image': [
                'Analyze image content (OCR if needed)',
                'Extract any text or data',
                'File in appropriate category'
            ],
            'archive': [
                'Extract archive contents',
                'Process each extracted file',
                'Clean up after extraction'
            ],
            'unknown': [
                'Identify file type and content',
                'Determine appropriate processing',
                'Take necessary actions'
            ]
        }
        return actions.get(file_type, actions['unknown'])


def main():
    """Main entry point for running the filesystem watcher."""
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = './AI_Employee_Vault'
    
    if len(sys.argv) > 2:
        drop_folder = sys.argv[2]
    else:
        drop_folder = None  # Will default to vault/Drop_Folder
    
    print(f"AI Employee - Filesystem Watcher v0.1")
    print(f"Vault: {Path(vault_path).absolute()}")
    print(f"Drop Folder: {drop_folder or '(vault/Drop_Folder)'}")
    print(f"Press Ctrl+C to stop\n")
    
    watcher = FilesystemWatcher(vault_path, drop_folder)
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nWatcher stopped.")


if __name__ == '__main__':
    main()
