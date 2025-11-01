#!/usr/bin/env python3
"""
Development daemon starter

Simple script to start the elevated daemon for development testing.
Run this as root to start the daemon.
"""

import os
import sys
import subprocess

def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print("❌ This script must be run as root!")
        print("Usage: sudo python start_daemon_dev.py")
        return False
    return True

def start_daemon():
    """Start the daemon"""
    print("🚀 Starting FadCrypt Elevated Daemon for development...")
    
    try:
        # Import and run daemon
        sys.path.insert(0, os.getcwd())
        from core.linux.elevated_daemon import main
        
        print("✅ Daemon module loaded successfully")
        print("🔧 Starting daemon (Ctrl+C to stop)...")
        
        # Run daemon
        main()
        
    except KeyboardInterrupt:
        print("\n🛑 Daemon stopped by user")
    except Exception as e:
        print(f"❌ Error starting daemon: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("FadCrypt Elevated Daemon - Development Starter")
    print("=" * 50)
    
    if not check_root():
        return
    
    start_daemon()

if __name__ == "__main__":
    main()