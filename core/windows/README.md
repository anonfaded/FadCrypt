# Windows Privilege Elevation System (Service-Based)

## Overview

FadCrypt for Windows implements a professional privilege escalation system using a Windows Service that runs with SYSTEM privileges. This provides seamless, persistent elevation for critical operations without repeated UAC prompts.

**Key Features:**

- ✅ **Persistent Authorization**: Automatic service elevation (FadCryptElevated service)
- ✅ **Professional Approach**: Uses Windows Service with SYSTEM privileges for secure operations
- ✅ **Minimal User Friction**: No prompts during normal operation after service installation
- ✅ **Secure Execution**: Runs with full SYSTEM privileges via Windows Service
- ✅ **Cross-Platform Compatibility**: Works on Windows 7+ and Windows Server 2008 R2+

## Architecture

### 1. **Elevated Service Client** (`core/windows/elevated_service_client.py`)

The `ElevatedServiceClient` class communicates with the FadCryptElevated Windows Service:

```python
# Get the client
from core.windows.elevated_service_client import get_elevated_client

client = get_elevated_client()

# Execute elevated operations via service
success, error = client.disable_system_tools()
success, error = client.protect_files([file1, file2])
success, error = client.unprotect_files([file1, file2])
```

**Communication:**
- Named pipe: `\\.\pipe\fadcrypt-elevated`
- JSON-RPC style protocol
- Automatic fallback if service unavailable

### 2. **Windows Elevated Service** (`core/windows/fadcrypt_elevated_service.py`)

Windows Service (FadCryptElevated) running with SYSTEM privileges that handles elevated operations:

**Operations Supported:**

- `disable-tools` - Disable Command Prompt, Task Manager, Registry Editor, Control Panel
- `enable-tools` - Re-enable previously disabled tools
- `protect-files` - Set file attributes (HIDDEN, SYSTEM, READONLY)
- `unprotect-files` - Remove file protection attributes

## Installation & Setup

### For Developers (Testing on Windows)

1. **Files already created:**

   - `core/windows/elevated_service_client.py` - Client for service communication
   - `core/windows/fadcrypt_elevated_service.py` - Windows Service implementation

2. **Install FadCryptElevated service** (requires admin):

```python
# Command line:
python core/windows/fadcrypt_elevated_service.py install

# Start the service:
python core/windows/fadcrypt_elevated_service.py start

# Stop or remove:
python core/windows/fadcrypt_elevated_service.py stop
python core/windows/fadcrypt_elevated_service.py remove
```

3. **Use the service from GUI:**

```python
if IS_WINDOWS:
    from core.windows.elevated_service_client import get_elevated_client

    client = get_elevated_client()
    if client.is_available():
        success, error = client.protect_files([file_path])
        # Check success/error
    else:
        print("FadCryptElevated service not installed")
```

### For Package Distribution

When building .exe with PyInstaller:

1. **Include service and client in spec file:**

```python
# In FadCrypt.spec
datas=[
    ('core/windows/fadcrypt_elevated_service.py', 'core/windows'),
    ('core/windows/elevated_service_client.py', 'core/windows'),
    # ... other files
]
hiddenimports=[
    'win32serviceutil',
    'win32service',
    'win32event',
    'servicemanager',
    'win32pipe',
    'win32file',
]
```

2. **InnoSetup installer** handles FadCryptElevated service installation:
   - Compiles service executable
   - Installs service via Windows Service Control Manager
   - Service starts automatically on Windows boot

3. **First-time setup**: Service installed during application setup

## How It Works (Technical Details)

### Scenario 1: Disable System Tools (During Monitoring Start)

```
User clicks "Start Monitoring"
    ↓
File Protection check needed? YES
    ↓
Elevated Service Client checks if FadCryptElevated service is available
    ↓
Service Available:
    1. Send operation request via named pipe (JSON-RPC)
    2. FadCryptElevated service (SYSTEM privileges) receives request
    3. Service processes operation (disable tools, protect files)
    4. Service returns success/error via named pipe
    ↓
Service Unavailable:
    1. Fallback: Try direct UAC via ShellExecuteW "runas"
    2. User prompted with single UAC dialog
    3. Helper script runs elevated
    ↓
Success → Continue monitoring
Failure → Show error, ask user to install FadCryptElevated service
```

### Scenario 2: Subsequent Operations (Same Session)

```
User attempts another operation requiring elevation
    ↓
Elevated Service Client connects to FadCryptElevated service
    ↓
Service Available:
    1. Send operation request via named pipe
    2. FadCryptElevated service processes it immediately
    3. (No UAC prompt - already running as SYSTEM)
    4. Returns result
    ↓
Result: Multiple operations without repeated prompts
```

## Advantages Over Alternatives

### vs. "Run as Administrator" at Startup

**Problem:** Entire app runs as admin (security risk)
**Our solution:** Only FadCryptElevated service runs with SYSTEM privileges

### vs. UAC Prompts for Every Operation

**Problem:** Poor UX, user fatigue
**Our solution:** Install service once (with UAC), then no prompts for operations

### vs. Task Scheduler Approach

**Problem:** Temporary tasks, registry pollution, slower execution
**Our solution:** Persistent Windows Service (FadCryptElevated) with direct named pipe communication

## File Attributes System (Windows Equivalent of chattr +i)

### Setting Protection

```python
# Equivalent to: chattr +i /path/to/file (Linux)
# Windows: Set attributes HIDDEN | SYSTEM | READONLY

FILE_ATTRIBUTE_HIDDEN    = 0x00000002
FILE_ATTRIBUTE_SYSTEM    = 0x00000004
FILE_ATTRIBUTE_READONLY  = 0x00000001

# Apply all three for maximum protection
new_attrs = FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM | FILE_ATTRIBUTE_READONLY
SetFileAttributesW(file_path, new_attrs)
```

### Effect

- File hidden in normal view
- User can't delete (readonly flag)
- Requires elevated privileges to modify
- Survives reboot

### Removing Protection

```python
# Remove protection attributes
FILE_ATTRIBUTE_NORMAL = 0x00000080

new_attrs = current_attrs & ~(HIDDEN | SYSTEM | READONLY)
new_attrs |= FILE_ATTRIBUTE_NORMAL

SetFileAttributesW(file_path, new_attrs)
```

## Registry Operations for Tool Disabling

### Disable Command Prompt

```
HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\System
  DisableCMD = 1 (REG_DWORD)
```

### Disable Task Manager

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System
  DisableTaskMgr = 1 (REG_DWORD)
```

### Disable Registry Editor

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System
  DisableRegistryTools = 1 (REG_DWORD)
```

### Disable Control Panel

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer
  NoControlPanel = 1 (REG_DWORD)
```

### Disable PowerShell Execution

```
HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\PowerShell
  ExecutionPolicy = 0 (REG_DWORD)  [0=Restricted, 1=AllSigned, 2=RemoteSigned, 3=Unrestricted]
```

These are re-enabled by deleting the values or setting to appropriate default values.

## Error Handling & Fallbacks

```python
# Best case: FadCryptElevated Windows Service available (no prompts)
# ↓ Fails if service not installed
# Fallback 1: Direct UAC ShellExecuteW (single prompt)
# ↓ Fails if not running on Windows or ctypes unavailable
# Fallback 2: Warning to user (no elevation possible)
```

## Security Considerations

### ✅ Secure Design

- FadCryptElevated service validates all operations
- Service runs as SYSTEM (highest privilege, isolated)
- Operations logged for audit trail
- Named pipe communication authenticated
- Service auto-starts with Windows boot
- Client validates service responses

### ⚠️ Limitations

- Windows only (by design)
- Requires Windows Vista or later (Service Control Manager)
- FadCryptElevated service must be installed (done during setup)
- User must have administrator account (not required to be current user)
- Some antivirus software may block service communication

### 🔒 Recommendations

- Run app with limited user (FadCryptElevated handles elevation)
- Monitor Windows Services for any unauthorized modifications
- Regularly review disabled tools settings
- Uninstall properly to remove service and re-enable tools
- Keep FadCryptElevated service running for seamless operation

## Testing on Linux (Mock Mode)

For development on Linux (cross-platform testing):

```python
python3 FadCrypt.py --windows  # Enable mock Windows mode
```

This loads mock implementations from `win_compat.py` and `win_mock.py`.

## Comparison: Linux vs Windows

| Feature               | Linux (PolicyKit)           | Windows (Windows Service)                |
| --------------------- | --------------------------- | ---------------------------------------- |
| **Elevation Method**  | Polkit authorization        | Windows Service (FadCryptElevated)       |
| **Privilege Level**   | Requested per operation     | Service runs with SYSTEM privileges      |
| **File Immutability** | `chattr +i` (filesystem)    | File attributes (HIDDEN/SYSTEM/READONLY) |
| **System Tool Lock**  | `chmod 000` + `chattr +i`   | Registry policies                        |
| **Persistence**       | `allow_active=yes`          | Windows Service auto-starts              |
| **User Experience**   | One sudo prompt per session | Service install prompt, no operation prompts |
| **Communication**     | Direct command execution    | Named pipe (\\.\pipe\fadcrypt-elevated)  |
| **Availability**      | Linux 3.0+                  | Windows Vista+ (Service Control Manager) |
| **Complexity**        | Lower (polkit built-in)     | Moderate (named pipes + service)         |

## Implementation Checklist

- [x] Create `core/windows/elevated_service_client.py` ✅
- [x] Create `core/windows/fadcrypt_elevated_service.py` ✅
- [x] Update `core/file_protection.py` to use service client ✅
- [x] Update Windows main window to use service client ✅
- [x] Add service client imports to Windows UI components ✅
- [x] Test on Windows 10/11 with service running ✅
- [x] Update PyInstaller spec to include service files ✅
- [x] Create Windows installer with service installation ✅
- [x] Add comprehensive logging for debugging ✅

## Troubleshooting

### Issue: "FadCryptElevated service not available" Error

**Cause:** Service not installed or not running
**Solution:** Install service via `python core/windows/fadcrypt_elevated_service.py install`
**Or:** Start service via Windows Services app (services.msc)

### Issue: "Access Denied" Error

**Cause:** Service not running with SYSTEM privileges
**Solution:** Restart service via `python core/windows/fadcrypt_elevated_service.py restart`

### Issue: Operations Take Too Long

**Cause:** Service processing large file lists or slow system
**Solution:** Check Windows Event Viewer for service logs

### Issue: Tools Still Accessible After Disable

**Cause:** Registry policies not applied correctly
**Solution:** Restart FadCrypt to reapply registry settings

## Future Enhancements

1. **Named Pipe Optimization** - Batch multiple operations
2. **Service Status Monitoring** - Real-time health checks
3. **Driver-Level Protection** - File system filter driver (complex, enterprise-grade)
4. **Azure AD Integration** - For enterprise MDM scenarios

## References

- [Windows Named Pipes Documentation](https://docs.microsoft.com/en-us/windows/win32/ipc/named-pipes)
- [Windows Service Documentation](https://docs.microsoft.com/en-us/windows/win32/services/services)
- [File Attributes Constants](https://docs.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants)
- [Windows Registry Group Policy](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings)
- [Windows Registry Group Policy](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings)
