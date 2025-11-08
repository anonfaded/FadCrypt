"""
Batch Coordinator for Windows Context Menu Operations

When multiple files/folders are selected and a context menu command is invoked,
Windows calls the command separately for each item. This module coordinates
those calls to show a single password prompt and process all items together.
"""

import os
import sys
import json
import time
import tempfile
import threading
from pathlib import Path
from datetime import datetime, timedelta

class BatchCoordinator:
    """Manages batch operations from context menu calls"""
    
    # Coordination file timeout (how long to wait for additional files before processing)
    COORDINATION_TIMEOUT = 2.0  # seconds
    # Batch operation marker file
    BATCH_MARKER_FILENAME = "batch_coordinator_{}.json"
    
    def __init__(self, operation: str, timeout: float = None):
        """
        Initialize coordinator for a batch operation.
        
        Args:
            operation: 'lock' or 'unlock'
            timeout: How long to wait for additional files (seconds)
        """
        self.operation = operation.lower()
        self.timeout = timeout or self.COORDINATION_TIMEOUT
        self.batch_dir = os.path.join(tempfile.gettempdir(), 'FadCrypt', 'batch')
        os.makedirs(self.batch_dir, exist_ok=True)
        
    def get_batch_file(self) -> str:
        """Get the batch coordinator file path for current session/operation"""
        # Use operation as part of filename to distinguish lock vs unlock
        marker_file = self.BATCH_MARKER_FILENAME.format(self.operation)
        return os.path.join(self.batch_dir, marker_file)
    
    def collect_paths(self, current_path: str) -> tuple:
        """
        Collect all paths for this batch operation.
        
        Args:
            current_path: The current file/folder path being added
            
        Returns:
            Tuple of (all_paths_list, is_primary_caller)
            - all_paths_list: List of all collected paths
            - is_primary_caller: True if this is the first caller (should show UI)
        """
        batch_file = self.get_batch_file()
        is_primary = False
        all_paths = []
        
        try:
            # Check if batch file already exists
            if os.path.exists(batch_file):
                # Read existing paths
                with open(batch_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_paths = data.get('paths', [])
                    creation_time = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
                    
                    # Check if batch is too old (timeout exceeded)
                    if datetime.now() - creation_time > timedelta(seconds=self.timeout):
                        # Old batch, start a new one
                        is_primary = True
                        all_paths = [current_path]
                        creation_time = datetime.now()
                    else:
                        # Add current path if not already present
                        if current_path not in all_paths:
                            all_paths.append(current_path)
                    
                    # Update batch file with new paths and extended timeout
                    data = {
                        'operation': self.operation,
                        'paths': list(set(all_paths)),  # Deduplicate
                        'created_at': creation_time.isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'count': len(set(all_paths))
                    }
                    with open(batch_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
            else:
                # First call in this batch
                is_primary = True
                all_paths = [current_path]
                
                data = {
                    'operation': self.operation,
                    'paths': all_paths,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'count': 1
                }
                with open(batch_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            
            return all_paths, is_primary
            
        except Exception as e:
            # On error, treat as primary (fail-safe)
            print(f"[BATCH COORDINATOR] Error: {e}", flush=True, file=sys.stderr)
            return [current_path], True
    
    def wait_for_additional_paths(self) -> list:
        """
        Wait for additional file selection calls from other context menu invocations.
        
        Returns:
            List of all collected paths after timeout
        """
        batch_file = self.get_batch_file()
        start_time = time.time()
        last_count = 0
        stable_count = 0
        
        try:
            while time.time() - start_time < self.timeout:
                time.sleep(0.1)  # Check every 100ms
                
                if os.path.exists(batch_file):
                    with open(batch_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        current_count = data.get('count', 0)
                        
                        # If count hasn't changed for 300ms, assume all files collected
                        if current_count == last_count:
                            stable_count += 1
                            if stable_count >= 3:  # 3 * 100ms = 300ms stable
                                return data.get('paths', [])
                        else:
                            stable_count = 0
                            last_count = current_count
            
            # Timeout reached, return whatever we have
            if os.path.exists(batch_file):
                with open(batch_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('paths', [])
            
            return []
            
        except Exception as e:
            print(f"[BATCH COORDINATOR] Wait error: {e}", flush=True, file=sys.stderr)
            return []
    
    def finalize(self):
        """Clean up the batch coordinator files"""
        batch_file = self.get_batch_file()
        try:
            if os.path.exists(batch_file):
                os.remove(batch_file)
        except Exception as e:
            print(f"[BATCH COORDINATOR] Cleanup error: {e}", flush=True, file=sys.stderr)


def coordinate_batch_operation(operation: str, first_path: str) -> tuple:
    """
    High-level function to coordinate a batch operation.
    
    Args:
        operation: 'lock' or 'unlock'
        first_path: The first file/folder being locked/unlocked
        
    Returns:
        Tuple of (all_paths_list, should_show_ui)
    """
    coordinator = BatchCoordinator(operation)
    
    # Collect this path with others
    all_paths, is_primary = coordinator.collect_paths(first_path)
    
    if is_primary:
        # This is the first context menu call - wait for others
        final_paths = coordinator.wait_for_additional_paths()
        coordinator.finalize()
        return final_paths, True
    else:
        # This is a secondary call - the primary will handle UI
        return all_paths, False
