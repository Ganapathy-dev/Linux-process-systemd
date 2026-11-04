# Linux Process Management

## Project Overview
Configured and deployed a Python background worker
using Linux systemd service management.

## Technologies
- Linux (Ubuntu / WSL2)
- Python 3
- systemd
- Bash

## Implementation
1. Created a Python background worker.
2. Configured a systemd service.
3. Configured environment variables.
4. Configured automatic restart.
5. Tested graceful shutdown using SIGTERM.
6. Tested forced termination using SIGKILL.
7. Enabled automatic startup at boot.
8. Verified service persistence after reboot.

## Service Details
Service: testpress-worker
User: labuser
Working Directory: /opt/testpress-worker
Application: app.py

## Evidence
Screenshots are available in the evidence/ directory.

## Verification
- Service active
- Service enabled
- Process running
- Heartbeat logs verified
- Automatic restart verified
- Reboot persistence verified
