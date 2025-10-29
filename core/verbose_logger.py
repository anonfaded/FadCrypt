"""
Verbose Logger

Centralized logging utility that respects --verbose flag.
Only prints debug/info logs when --verbose is passed.
"""

import sys

# Check if verbose mode is enabled
VERBOSE_ENABLED = '--verbose' in sys.argv


def vlog(message: str, force: bool = False):
    """
    Print a verbose log message.
    
    Args:
        message: The message to print
        force: If True, always print regardless of verbose mode
    """
    if force or VERBOSE_ENABLED:
        print(message)


def is_verbose() -> bool:
    """Check if verbose mode is enabled"""
    return VERBOSE_ENABLED
