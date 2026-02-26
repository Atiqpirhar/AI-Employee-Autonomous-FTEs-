#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Triggers Qwen Code to process pending items.

The orchestrator monitors the Needs_Action and Approved folders and triggers
Qwen Code to process items. It implements the human-in-the-loop pattern
by handling approved actions and moving completed items to Done.

Usage:
    python orchestrator.py [vault_path]
    
Example:
    python orchestrator.py ./AI_Employee_Vault
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Orchestrator:
    """
    Orchestrates the AI Employee workflow.
    
    Responsibilities:
    1. Monitor Needs_Action folder for new items
    2. Trigger Qwen Code to process pending items
    3. Handle approved actions from Approved folder
    4. Move completed items to Done folder
    5. Update Dashboard.md with recent activity
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.rejected = self.vault_path / 'Rejected'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure all folders exist
        for folder in [self.needs_action, self.approved, self.done, 
                       self.pending_approval, self.rejected, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.qwen_command = self._find_qwen()
        
    def _find_qwen(self) -> str:
        """Find the Qwen Code command."""
        # Try common locations
        possible_commands = ['qwen', 'qwen-code', '@alibaba/qwen-code']

        for cmd in possible_commands:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.logger.info(f"Found Qwen Code: {cmd}")
                    return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        # Try with npx (common for npm-installed qwen-code)
        try:
            result = subprocess.run(
                ['npx', 'qwen', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("Found Qwen Code: npx qwen")
                return 'npx qwen'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        self.logger.warning("Qwen Code not found in PATH. Using 'qwen' command.")
        return 'qwen'
    
    def get_pending_items(self) -> List[Path]:
        """Get list of pending items in Needs_Action folder."""
        try:
            items = [f for f in self.needs_action.iterdir() 
                    if f.is_file() and f.suffix == '.md' and not f.name.startswith('.')]
            return sorted(items, key=lambda x: x.stat().st_mtime)
        except Exception as e:
            self.logger.error(f"Error scanning Needs_Action: {e}")
            return []
    
    def get_approved_items(self) -> List[Path]:
        """Get list of approved items awaiting action."""
        try:
            items = [f for f in self.approved.iterdir() 
                    if f.is_file() and f.suffix == '.md']
            return sorted(items, key=lambda x: x.stat().st_mtime)
        except Exception as e:
            self.logger.error(f"Error scanning Approved: {e}")
            return []
    
    def process_with_qwen(self, prompt: str) -> Tuple[bool, str]:
        """
        Send a prompt to Qwen Code and get the response.

        Args:
            prompt: The prompt to send to Qwen Code

        Returns:
            Tuple of (success, response or error message)
        """
        try:
            # Handle command that may contain spaces (e.g., 'npx qwen')
            if ' ' in self.qwen_command:
                cmd_parts = self.qwen_command.split()
            else:
                cmd_parts = [self.qwen_command]
            
            # Qwen Code uses -p/--prompt for non-interactive mode
            # and doesn't have --add-dir, it works in current directory
            cmd = cmd_parts + [
                '-p', prompt  # Use -p for prompt mode
            ]

            self.logger.info(f"Calling Qwen Code: {prompt[:50]}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=(os.name == 'nt'),  # Use shell on Windows for npx
                cwd=str(self.vault_path)  # Set working directory to vault
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                error_msg = result.stderr or f"Exit code: {result.returncode}"
                self.logger.error(f"Qwen Code error: {error_msg}")
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = "Qwen Code timed out after 5 minutes"
            self.logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = f"Qwen Code not found. Tried: {self.qwen_command}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def log_activity(self, action: str, details: str, status: str = 'success'):
        """Log an activity to the daily log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_folder / f"{today}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "status": status
        }
        
        # Append to log file (simple JSON lines format)
        import json
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def update_dashboard(self, action: str, details: str):
        """Update the Dashboard.md with recent activity."""
        try:
            if not self.dashboard.exists():
                self.logger.warning("Dashboard.md not found")
                return
            
            content = self.dashboard.read_text()
            
            # Find the Recent Activity section and add new entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            new_entry = f"- [{timestamp}] {action}: {details}"
            
            # Look for the activity section
            if '*No recent activity*' in content:
                content = content.replace('*No recent activity*', new_entry)
            elif '## Recent Activity' in content:
                # Insert after the header
                lines = content.split('\n')
                new_lines = []
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if line == '## Recent Activity':
                        # Skip any existing "No recent activity" line
                        if i + 1 < len(lines) and '*No recent activity*' in lines[i + 1]:
                            new_lines.append(new_entry)
                            new_lines.append('')  # blank line
                        else:
                            new_lines.append(new_entry)
                content = '\n'.join(new_lines)
            
            self.dashboard.write_text(content)
            self.logger.debug("Dashboard updated")
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
    
    def move_to_done(self, filepath: Path, reason: str = ''):
        """Move a file to the Done folder."""
        try:
            dest = self.done / filepath.name
            shutil.move(str(filepath), str(dest))
            self.logger.info(f"Moved to Done: {filepath.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error moving {filepath.name} to Done: {e}")
            return False
    
    def move_to_rejected(self, filepath: Path, reason: str = ''):
        """Move a file to the Rejected folder."""
        try:
            dest = self.rejected / filepath.name
            # Add rejection reason to file
            content = filepath.read_text()
            content += f"\n\n---\n## Rejected\nReason: {reason}\nDate: {datetime.now().isoformat()}\n"
            dest.write_text(content)
            shutil.move(str(filepath), str(dest))
            self.logger.info(f"Moved to Rejected: {filepath.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error moving {filepath.name} to Rejected: {e}")
            return False
    
    def process_needs_action(self):
        """Process all items in Needs_Action folder."""
        items = self.get_pending_items()
        
        if not items:
            self.logger.debug("No items in Needs_Action")
            return
        
        self.logger.info(f"Found {len(items)} item(s) in Needs_Action")
        
        # Build prompt for Claude
        item_list = '\n'.join([f"- {item.name}" for item in items])
        
        prompt = f"""You are the AI Employee. Process the following pending items in the Needs_Action folder:

{item_list}

For each item:
1. Read the file content
2. Understand what action is needed
3. If the action requires approval, create a file in /Pending_Approval/
4. If the action can be done directly, do it and move the file to /Done/
5. If you need more information, update the file with questions

Reference the Company_Handbook.md for rules and guidelines.
Reference the Business_Goals.md for context on priorities.

After processing, update the Dashboard.md with a summary of what was done."""

        success, response = self.process_with_qwen(prompt)

        if success:
            self.log_activity('process_needs_action', f'Processed {len(items)} items')
            self.update_dashboard('Processed', f'{len(items)} pending item(s)')
        else:
            self.log_activity('process_needs_action', f'Failed: {response}', 'error')
    
    def process_approved(self):
        """Process approved items that are ready for action."""
        items = self.get_approved_items()
        
        if not items:
            self.logger.debug("No items in Approved")
            return
        
        self.logger.info(f"Found {len(items)} approved item(s)")
        
        for item in items:
            # Read the approval file to understand the action
            content = item.read_text()
            
            # Build prompt for Claude to execute the approved action
            prompt = f"""You are the AI Employee. The following action has been APPROVED by a human:

File: {item.name}

Content:
{content}

Execute this approved action now. After completing the action:
1. Log the action in the daily log
2. Move this file to /Done/
3. Update the Dashboard.md

If the action cannot be completed, move the file to /Rejected/ with an explanation."""

            success, response = self.process_with_qwen(prompt)

            if success:
                self.log_activity('execute_approved', f'Executed: {item.name}')
                self.update_dashboard('Completed', f'Approved action: {item.name}')
                # Move to done
                self.move_to_done(item)
            else:
                self.log_activity('execute_approved', f'Failed: {response}', 'error')
    
    def run_once(self):
        """Run one iteration of processing."""
        self.logger.info("=== Orchestrator Run ===")
        
        # First process any approved items (higher priority)
        self.process_approved()
        
        # Then process needs_action items
        self.process_needs_action()
        
        self.logger.info("=== Orchestrator Run Complete ===")
    
    def run_continuous(self, check_interval: int = 60):
        """
        Run the orchestrator continuously.
        
        Args:
            check_interval: How often to check for new items (in seconds)
        """
        import time
        
        self.logger.info(f"Starting continuous orchestrator (interval: {check_interval}s)")
        
        try:
            while True:
                self.run_once()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")


# Import shutil for move operations
import shutil


def main():
    """Main entry point for the orchestrator."""
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = './AI_Employee_Vault'
    
    # Check for --continuous flag
    continuous = '--continuous' in sys.argv or '-c' in sys.argv
    
    print(f"AI Employee - Orchestrator v0.1")
    print(f"Vault: {Path(vault_path).absolute()}")
    print(f"Mode: {'Continuous' if continuous else 'Single run'}")
    print(f"Press Ctrl+C to stop\n")
    
    orchestrator = Orchestrator(vault_path)
    
    if continuous:
        orchestrator.run_continuous()
    else:
        orchestrator.run_once()


if __name__ == '__main__':
    main()
