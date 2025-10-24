"""
FadCrypt Version Information
Single source of truth for version across the application and build system.
"""

__version__ = "2.0.0"
__version_code__ = 5  # Increment this for each release

# Package metadata
PACKAGE_NAME = "fadcrypt"
PACKAGE_DESCRIPTION = "Application locker and monitor for Linux"
PACKAGE_LONG_DESCRIPTION = """FadCrypt is a cross-platform GUI application that helps you lock and
 monitor applications with password protection and encrypted configuration.
 .
 Features include:
  - Lock/unlock specific applications
  - Password-protected monitoring
  - System tray integration
  - Auto-start on login support
  - Built-in mini snake game"""

# Maintainer information
MAINTAINER_NAME = "Faded"
MAINTAINER_EMAIL = "fadedhood@proton.me"
MAINTAINER_ORG = "FadSec Lab"
MAINTAINER_FULL = f"{MAINTAINER_NAME} <{MAINTAINER_EMAIL}>"
