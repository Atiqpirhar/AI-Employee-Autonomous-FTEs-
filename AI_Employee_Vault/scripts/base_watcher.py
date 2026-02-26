#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all AI Employee watchers.

Watchers are lightweight Python scripts that run continuously in the background,
monitoring various inputs (Gmail, WhatsApp, filesystems) and creating actionable
files for Claude Code to process.

Usage:
    Subclass this base class and implement the abstract methods.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    A watcher monitors a specific data source and creates action files
    in the Needs_Action folder when new items are detected.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: How often to check for updates (in seconds)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_ids: set = set()
        self._running = False
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the data source for new items.
        
        Returns:
            List of new items that need processing
            
        Example:
            For Gmail: List of new email message objects
            For FileSystem: List of new file paths
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file for an item.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created action file, or None if creation failed
            
        The action file should include:
            - YAML frontmatter with type, priority, status, timestamps
            - Content section with the item details
            - Suggested actions section with checkboxes
        """
        pass
    
    def _generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: Type prefix (e.g., 'EMAIL', 'FILE', 'WHATSAPP')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Sanitize unique_id to be filesystem-safe
        safe_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in unique_id)
        return f"{prefix}_{safe_id}_{timestamp}.md"
    
    def _write_action_file(self, filename: str, content: str) -> Path:
        """
        Write content to an action file.
        
        Args:
            filename: Name of the file to create
            content: Markdown content to write
            
        Returns:
            Path to the created file
        """
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created action file: {filepath.name}")
        return filepath
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C) or stop() is called.
        """
        self._running = True
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path.absolute()}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        
        try:
            while self._running:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f"Found {len(items)} new item(s)")
                        for item in items:
                            try:
                                self.create_action_file(item)
                            except Exception as e:
                                self.logger.error(f"Error creating action file: {e}")
                    else:
                        self.logger.debug("No new items")
                except Exception as e:
                    self.logger.error(f"Error checking for updates: {e}")
                
                # Sleep in small increments to allow for graceful shutdown
                for _ in range(self.check_interval):
                    if not self._running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the watcher loop."""
        self._running = False
        self.logger.info(f"Stopping {self.__class__.__name__}")
    
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._running


def main():
    """
    Example usage and testing of the base watcher.
    
    This demonstrates how to subclass BaseWatcher.
    """
    
    class TestWatcher(BaseWatcher):
        """Test watcher that generates sample action files."""
        
        def __init__(self, vault_path: str):
            super().__init__(vault_path, check_interval=30)
            self.counter = 0
        
        def check_for_updates(self) -> List[dict]:
            # For testing: generate one item per check
            self.counter += 1
            if self.counter <= 1:  # Only generate one test item
                return [{'id': f'test_{self.counter}', 'content': 'Test item'}]
            return []
        
        def create_action_file(self, item: dict) -> Optional[Path]:
            content = f"""---
type: test
id: {item['id']}
created: {datetime.now().isoformat()}
priority: low
status: pending
---

# Test Action Item

This is a test action file created by TestWatcher.

## Content
{item['content']}

## Suggested Actions
- [ ] Review this item
- [ ] Take appropriate action
- [ ] Move to /Done when complete
"""
            filename = self._generate_filename('TEST', item['id'])
            return self._write_action_file(filename, content)
    
    # Run the test watcher
    import sys
    if len(sys.argv) > 1:
        vault = sys.argv[1]
    else:
        vault = './AI_Employee_Vault'
    
    watcher = TestWatcher(vault)
    watcher.run()


if __name__ == '__main__':
    main()
