"""
Statistics Manager - Calculates and caches statistics
Parses config and activity logs to generate insights
Includes duration tracking and chart data generation
"""

import json
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict


class StatisticsManager:
    """Manages statistics calculation and caching"""
    
    def __init__(self, config_folder: str):
        self.config_folder = config_folder
        self.config_file = os.path.join(config_folder, 'apps_config.json')
        self.activity_log_file = os.path.join(config_folder, 'activity.log')
        self.stats_cache_file = os.path.join(config_folder, 'statistics.json')
        self.metadata_file = os.path.join(config_folder, 'metadata.json')
        self.cache_duration = 60  # seconds - recalculate if older than this
        
        # Initialize session metadata on first creation (once per app session)
        self._init_session_metadata()
        
    def _init_session_metadata(self):
        """Initialize session metadata (called once per app startup)"""
        try:
            from core.file_protection import safe_write_to_protected_file
            # Create fresh metadata file with current startup time
            startup_data = {'first_startup': datetime.now().isoformat()}
            content = json.dumps(startup_data, indent=2)
            safe_write_to_protected_file(self.metadata_file, content)
        except:
            pass
    
    def get_session_uptime(self) -> Dict:
        """Get FadCrypt session uptime (current app instance only)"""
        # Load the startup time from metadata (created fresh on app startup)
        startup_time = datetime.now()
        
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                    startup_time = datetime.fromisoformat(metadata.get('first_startup', datetime.now().isoformat()))
        except:
            pass
        
        # Calculate uptime
        uptime = datetime.now() - startup_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        total_hours = uptime.total_seconds() / 3600
        total_minutes = uptime.total_seconds() / 60
        
        # Format uptime showing only non-zero values (e.g., "30s", then "1m 30s", then "1h 5m 30s")
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or len(parts) == 0:  # Always show seconds if nothing else to show
            parts.append(f"{seconds}s")
        uptime_formatted = " ".join(parts)
        
        return {
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_minutes': int(total_minutes),
            'uptime_hours': round(total_hours, 2),
            'uptime_formatted': uptime_formatted,
            'first_startup': startup_time.isoformat(),
            'current_time': datetime.now().isoformat()
        }
    
    def _get_config(self) -> Dict:
        """Load unified config"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {'applications': [], 'locked_files_and_folders': []}
        return {'applications': [], 'locked_files_and_folders': []}
    
    def _get_activity_events(self) -> List[Dict]:
        """Load all activity events"""
        if not os.path.exists(self.activity_log_file):
            return []
        
        events = []
        try:
            with open(self.activity_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        except:
            pass
        return events
    
    def calculate_stats(self) -> Dict:
        """Calculate all statistics"""
        config = self._get_config()
        events = self._get_activity_events()
        
        apps = config.get('applications', [])
        locked_items = config.get('locked_files_and_folders', [])
        
        # Basic counts
        total_apps = len(apps)
        total_locked_items = len(locked_items)
        total_items = total_apps + total_locked_items
        
        # Calculate lock/unlock counts
        total_locks = sum(app.get('unlock_count', 0) for app in apps)
        total_locks += sum(item.get('unlock_count', 0) for item in locked_items)
        
        # Most locked items - handle both structures
        most_locked = sorted(
            [(app.get('name', 'Unknown'), app.get('unlock_count', 0)) for app in apps] +
            [(item.get('path', 'Unknown'), item.get('unlock_count', 0)) for item in locked_items],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Event statistics
        lock_events = len([e for e in events if 'lock' in e.get('event_type', '')])
        unlock_events = len([e for e in events if e.get('event_type') == 'unlock'])  # Only successful unlocks
        failed_attempts = len([e for e in events if e.get('event_type') == 'failed_unlock'])
        
        # Peak lock hour
        lock_hours = [datetime.fromisoformat(e['timestamp']).hour 
                     for e in events if 'lock' in e.get('event_type', '')]
        peak_hour = max(set(lock_hours), key=lock_hours.count) if lock_hours else 0
        
        # Lock streak
        lock_streak = self._calculate_lock_streak(events)
        
        # Protection percentage
        protection_pct = (total_locked_items / total_items * 100) if total_items > 0 else 0
        
        # Last activity
        last_activity = None
        if events:
            last_event = events[-1]
            last_activity = {
                'type': last_event.get('event_type', 'unknown'),
                'item': last_event.get('item_name', 'N/A'),
                'timestamp': last_event.get('timestamp')
            }
        
        stats = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_items': total_items,
                'total_applications': total_apps,
                'total_locked_items': total_locked_items,
                'protection_percentage': round(protection_pct, 1),
                'lock_streak_days': lock_streak
            },
            'activity': {
                'total_lock_events': lock_events,
                'total_unlock_events': unlock_events,
                'failed_unlock_attempts': failed_attempts,
                'peak_lock_hour': peak_hour,
                'last_activity': last_activity
            },
            'items': {
                'most_locked': most_locked[:5],  # Top 5
                'total_unlock_count': total_locks
            }
        }
        
        return stats
    
    def _calculate_lock_streak(self, events: List[Dict]) -> int:
        """Calculate consecutive days with at least one lock event"""
        lock_dates = set()
        for event in events:
            if 'lock' in event.get('event_type', ''):
                try:
                    ts = datetime.fromisoformat(event['timestamp'])
                    lock_dates.add(ts.date())
                except:
                    pass
        
        if not lock_dates:
            return 0
        
        sorted_dates = sorted(lock_dates)
        streak = 1
        max_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] - sorted_dates[i-1] == timedelta(days=1):
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1
        
        # Check if current streak continues to today
        today = datetime.now().date()
        if sorted_dates[-1] == today or sorted_dates[-1] == today - timedelta(days=1):
            return max_streak
        return 0
    
    def get_stats(self, use_cache: bool = True) -> Dict:
        """Get statistics (use cache if valid)"""
        if use_cache and os.path.exists(self.stats_cache_file):
            try:
                with open(self.stats_cache_file, 'r') as f:
                    cached = json.load(f)
                # Check if cache is still fresh
                cache_time = datetime.fromisoformat(cached.get('generated_at', ''))
                if datetime.now() - cache_time < timedelta(seconds=self.cache_duration):
                    return cached
            except:
                pass
        
        # Calculate and cache
        stats = self.calculate_stats()
        try:
            from core.file_protection import safe_write_to_protected_file
            content = json.dumps(stats, indent=2)
            safe_write_to_protected_file(self.stats_cache_file, content)
        except:
            pass
        
        return stats
    
    def get_pie_chart_data(self) -> Dict:
        """Get data for item type distribution pie chart with category items"""
        config = self._get_config()
        
        apps = config.get('applications', [])
        files_list = []
        folders_list = []
        
        for item in config.get('locked_files_and_folders', []):
            if item.get('type') == 'file':
                files_list.append(item)
            elif item.get('type') == 'folder':
                folders_list.append(item)
        
        # Build lists of names for each category
        app_names = [app.get('name', 'Unknown') for app in apps]
        file_names = [item.get('path', 'Unknown').split('/')[-1] for item in files_list]
        folder_names = [item.get('path', 'Unknown').split('/')[-1] for item in folders_list]
        
        return {
            'labels': ['Applications', 'Files', 'Folders'],
            'data': [len(apps), len(files_list), len(folders_list)],
            'category_items': {
                0: app_names,
                1: file_names,
                2: folder_names
            }
        }
    
    def get_lock_unlock_timeline(self, days: int = 7) -> Dict:
        """Get lock/unlock events over time for line chart"""
        events = self._get_activity_events()
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        # Group events by day and type
        timeline = defaultdict(lambda: {'locks': 0, 'unlocks': 0})
        
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['timestamp'])
                if event_time >= start_date:
                    date_key = event_time.date().isoformat()
                    event_type = event.get('event_type', '').lower()
                    
                    if 'lock' in event_type and 'unlock' not in event_type:
                        timeline[date_key]['locks'] += 1
                    elif 'unlock' in event_type:
                        timeline[date_key]['unlocks'] += 1
            except:
                pass
        
        # Fill in missing dates with zeros
        all_dates = []
        for i in range(days, -1, -1):
            date = (now - timedelta(days=i)).date().isoformat()
            all_dates.append(date)
            if date not in timeline:
                timeline[date] = {'locks': 0, 'unlocks': 0}
        
        return {
            'dates': all_dates,
            'locks': [timeline[d]['locks'] for d in all_dates],
            'unlocks': [timeline[d]['unlocks'] for d in all_dates]
        }
    
    def get_duration_stats(self, monitoring_active: bool = False) -> Dict:
        """
        Calculate duration statistics from activity logs
        
        Args:
            monitoring_active: If True, includes current durations for locked/unlocked items
        """
        events = self._get_activity_events()
        
        # Find lock/unlock pairs to calculate durations
        item_sessions = defaultdict(list)
        
        for event in events:
            item_name = event.get('item_name', 'Unknown')
            event_type = event.get('event_type', '').lower()
            timestamp = event.get('timestamp')
            
            # Skip generic "all_items" events - they don't represent specific item durations
            if item_name == 'all_items':
                continue
            
            if item_name and timestamp:
                if 'lock' in event_type and 'unlock' not in event_type:
                    item_sessions[item_name].append({
                        'type': 'lock',
                        'timestamp': datetime.fromisoformat(timestamp)
                    })
                elif 'unlock' in event_type:
                    item_sessions[item_name].append({
                        'type': 'unlock',
                        'timestamp': datetime.fromisoformat(timestamp)
                    })
        
        # Calculate durations
        durations = {
            'by_item': {},
            'averages': {
                'avg_lock_duration_seconds': 0,
                'avg_unlock_duration_seconds': 0
            }
        }
        
        lock_durations = []
        unlock_durations = []
        
        for item_name, sessions in item_sessions.items():
            item_lock_durations = []
            item_unlock_durations = []
            
            sessions_sorted = sorted(sessions, key=lambda x: x['timestamp'])
            locked_since = None
            unlocked_since = None
            
            for session in sessions_sorted:
                if session['type'] == 'lock':
                    if unlocked_since:
                        # Calculate unlock duration
                        duration = (session['timestamp'] - unlocked_since).total_seconds()
                        item_unlock_durations.append(duration)
                        unlock_durations.append(duration)
                        unlocked_since = None
                    locked_since = session['timestamp']
                
                elif session['type'] == 'unlock':
                    if locked_since:
                        # Calculate lock duration
                        duration = (session['timestamp'] - locked_since).total_seconds()
                        item_lock_durations.append(duration)
                        lock_durations.append(duration)
                        locked_since = None
                    unlocked_since = session['timestamp']
            
            # Include current durations for items still locked/unlocked (LIVE UPDATE)
            # CRITICAL: Only if monitoring is active AND item is CURRENTLY in that state
            if monitoring_active:
                # Get current unlocked lists to verify item is ACTUALLY still unlocked/locked
                unlocked_apps = self._get_monitoring_state().get('unlocked_apps', [])
                unlocked_files = self._get_monitoring_state().get('unlocked_files', [])
                
                # For locked items: only include if still locked (NOT in unlocked lists)
                if locked_since:
                    is_currently_locked = item_name not in unlocked_apps
                    # For files, check by path in unlocked_files
                    # (item_name might just be basename, so we can't be 100% sure for files)
                    # But for apps, this check is reliable
                    
                    if is_currently_locked:
                        current_lock_duration = (datetime.now() - locked_since).total_seconds()
                        item_lock_durations.append(current_lock_duration)
                        lock_durations.append(current_lock_duration)
                
                # For unlocked items: only include if still unlocked (IN unlocked lists)
                if unlocked_since:
                    is_currently_unlocked = item_name in unlocked_apps
                    # For files, would need to check full path against unlocked_files
                    # But app name matching is reliable
                    
                    if is_currently_unlocked:
                        current_unlock_duration = (datetime.now() - unlocked_since).total_seconds()
                        item_unlock_durations.append(current_unlock_duration)
                        unlock_durations.append(current_unlock_duration)
            
            # Store item-specific stats
            # CRITICAL FIX: Only store stats if we have actual completed sessions
            # OR if monitoring is active (live sessions count)
            # This prevents showing stale "1 sessions" data when monitoring is stopped
            if item_lock_durations or item_unlock_durations:
                avg_lock = sum(item_lock_durations) / len(item_lock_durations) if item_lock_durations else 0
                avg_unlock = sum(item_unlock_durations) / len(item_unlock_durations) if item_unlock_durations else 0
                
                durations['by_item'][item_name] = {
                    'avg_lock_duration_seconds': round(avg_lock, 1),
                    'avg_unlock_duration_seconds': round(avg_unlock, 1),
                    'total_lock_sessions': len(item_lock_durations),
                    'total_unlock_sessions': len(item_unlock_durations)
                }
        
        # IMPORTANT: Check CURRENT state of ALL items (not just those with events)
        # This captures items that are locked by default when monitoring starts
        # CRITICAL: Only if monitoring is CURRENTLY ACTIVE (not from previous session)
        if monitoring_active:
            monitoring_start_time = self._get_monitoring_start_time()
            # If no start time found, use current time (monitoring just started)
            # This handles cases where stats are viewed immediately after monitoring starts
            if not monitoring_start_time:
                monitoring_start_time = datetime.now()
            
            # Verify this is a RECENT monitoring session
            # Allow flexibility: if start time is in future (clock skew) or within reasonable range
            # If more than 24 hours, skip this (prevents stale data from previous sessions)
            time_diff = (datetime.now() - monitoring_start_time).total_seconds()
            is_recent_session = time_diff >= -60 and time_diff < 86400  # -60 allows for clock skew
            
            if is_recent_session:
                config = self._get_config()
                unlocked_apps = self._get_monitoring_state().get('unlocked_apps', [])
                unlocked_files = self._get_monitoring_state().get('unlocked_files', [])
                
                # Check all apps
                for app in config.get('applications', []):
                    app_name = app.get('name')
                    if not app_name:
                        continue
                    
                    # Skip if already processed from events
                    if app_name in item_sessions:
                        continue
                    
                    # App is currently locked (not in unlocked_apps list)
                    if app_name not in unlocked_apps:
                        lock_duration = (datetime.now() - monitoring_start_time).total_seconds()
                        lock_durations.append(lock_duration)
                        durations['by_item'][app_name] = {
                            'avg_lock_duration_seconds': round(lock_duration, 1),
                            'avg_unlock_duration_seconds': 0,
                            'total_lock_sessions': 1,
                            'total_unlock_sessions': 0
                        }
                
                # Check all files/folders
                for item in config.get('locked_files_and_folders', []):
                    item_path = item.get('path', '')
                    if not item_path:
                        continue
                    
                    item_name = os.path.basename(item_path)
                    
                    # Skip if already processed from events
                    if item_name in item_sessions:
                        continue
                    
                    # Item is currently locked (not in unlocked_files list)
                    if item_path not in unlocked_files:
                        lock_duration = (datetime.now() - monitoring_start_time).total_seconds()
                        lock_durations.append(lock_duration)
                        durations['by_item'][item_name] = {
                            'avg_lock_duration_seconds': round(lock_duration, 1),
                            'avg_unlock_duration_seconds': 0,
                            'total_lock_sessions': 1,
                            'total_unlock_sessions': 0
                        }
        
        # Calculate overall averages
        if lock_durations:
            durations['averages']['avg_lock_duration_seconds'] = round(sum(lock_durations) / len(lock_durations), 1)
        if unlock_durations:
            durations['averages']['avg_unlock_duration_seconds'] = round(sum(unlock_durations) / len(unlock_durations), 1)
        
        return durations
    
    def _get_monitoring_state(self) -> Dict:
        """Get current monitoring state"""
        monitoring_state_file = os.path.join(self.config_folder, 'monitoring_state.json')
        if os.path.exists(monitoring_state_file):
            try:
                with open(monitoring_state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _get_monitoring_start_time(self) -> Optional[datetime]:
        """Get when monitoring was started for current session"""
        # Look for most recent 'start_monitoring' event
        events = self._get_activity_events()
        for event in reversed(events):  # Most recent first
            if event.get('event_type') == 'start_monitoring':
                try:
                    return datetime.fromisoformat(event.get('timestamp'))
                except:
                    pass
        return None
    
    def get_comprehensive_stats(self) -> Dict:
        """Get all statistics including charts and durations"""
        base_stats = self.get_stats(use_cache=False)
        
        # Check if monitoring is currently active
        monitoring_active = self._is_monitoring_active()
        
        return {
            'generated_at': datetime.now().isoformat(),
            'summary': base_stats.get('summary', {}),
            'activity': base_stats.get('activity', {}),
            'items': base_stats.get('items', {}),
            'pie_chart': self.get_pie_chart_data(),
            'timeline': self.get_lock_unlock_timeline(days=7),
            'durations': self.get_duration_stats(monitoring_active=monitoring_active),
            'session_uptime': self.get_session_uptime()
        }
    
    def _is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active"""
        monitoring_state_file = os.path.join(self.config_folder, 'monitoring_state.json')
        if os.path.exists(monitoring_state_file):
            try:
                with open(monitoring_state_file, 'r') as f:
                    state = json.load(f)
                return state.get('monitoring_active', False)
            except:
                pass
        return False
