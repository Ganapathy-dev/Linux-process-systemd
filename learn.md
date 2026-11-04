
# Linux Process Management – Running a Python Worker with systemd

A practical Linux project demonstrating how to deploy, manage and monitor a Python background worker using systemd.

## 1. Project Overview

This project demonstrates how to run a Python application as a Linux background service using **systemd**.

Instead of manually executing a Python script from the terminal, systemd manages the application as a service.

The configured service supports:

- Running in the background without keeping a terminal open.
- Starting automatically when the system boots.
- Restarting automatically if the application crashes.
- Graceful shutdown when receiving a termination signal.
- Centralized logging through the systemd journal.
- Running under a dedicated, non-root Linux user.

## 2. What is systemd?

**systemd** is the system and service manager used by many Linux distributions, including Ubuntu.

It is responsible for managing system services and other processes during system startup and normal operation.

Examples of services managed by systemd:

- SSH server
- Cron service
- Docker service
- Network services
- Custom Python background workers

In this project, systemd manages the `testpress-worker` Python application.

## 3. What is systemctl?

**systemctl** is the command-line utility used to communicate with systemd.

It provides commands to start, stop, restart, enable, disable and inspect services.

### Common Commands

| Command | Purpose |
|---|---|
| `sudo systemctl start SERVICE` | Start a service |
| `sudo systemctl stop SERVICE` | Stop a service |
| `sudo systemctl restart SERVICE` | Restart a service |
| `sudo systemctl status SERVICE` | Check service status |
| `sudo systemctl enable SERVICE` | Enable automatic startup at boot |
| `sudo systemctl disable SERVICE` | Disable automatic startup at boot |
| `systemctl is-active SERVICE` | Check whether a service is active |
| `systemctl is-enabled SERVICE` | Check whether a service is enabled |
| `sudo systemctl daemon-reload` | Reload systemd unit definitions |

## 4. What is a daemon?

A **daemon** is a background process that runs without requiring an interactive terminal session.

Examples:

- `sshd` – SSH server daemon
- `cron` – Scheduled task daemon
- `systemd-journald` – Logging service
- Python worker – Background application process

### Important Distinction

- A daemon is a background process.
- systemd is a service manager that can manage daemons.
- systemctl is the command-line utility used to communicate with systemd.

Not every background process is necessarily managed by systemd.

## 5. systemd Unit File Locations

To understand where systemd searches for unit files, execute:

```bash
systemd-analyze unit-paths
```

This command displays the directories systemd searches for unit files.

### Important Locations

| Directory | Purpose |
|---|---|
| `/etc/systemd/system/` | Administrator-created services and local overrides |
| `/run/systemd/system/` | Runtime unit files |
| `/usr/lib/systemd/system/` | System and package-provided unit files on many distributions |
| `/lib/systemd/system/` | Package-provided unit files on some distributions |

For this project, the custom service file is located at:

```text
/etc/systemd/system/testpress-worker.service
```

This is the recommended location for a system-wide custom service.

**Note:** Exact unit search paths vary between Linux distributions.

## 6. Why Are the Application and Service File in Different Locations?

The project uses two important locations.

### Application Location

```text
/opt/testpress-worker/app.py
```

### systemd Service Configuration

```text
/etc/systemd/system/testpress-worker.service
```

### Difference Between These Locations

| Location | Responsibility |
|---|---|
| `/opt/testpress-worker/` | Stores the deployed application |
| `/etc/systemd/system/` | Stores instructions for systemd about how to manage the application |

The service file tells systemd:

- Which user should execute the application.
- Which working directory to use.
- Which Python interpreter to execute.
- Where environment variables are stored.
- How to restart the application.

It is technically possible to execute an application directly from a Git repository.

However, keeping deployed applications under `/opt` separates application deployment from development files.

This separation makes deployment and maintenance easier to manage.

## 7. Difference Between start and enable

These two commands perform different operations.

### Start

```bash
sudo systemctl start testpress-worker
```

- Starts the service immediately.
- Does not automatically configure the service to start after a reboot.

### Enable

```bash
sudo systemctl enable testpress-worker
```

- Configures the service to start automatically during the appropriate system boot target.
- Does not necessarily start the service immediately.

### Start and Enable Together

```bash
sudo systemctl enable --now testpress-worker
```

This enables automatic startup and starts the service immediately.

## 8. Difference Between stop and disable

### Stop

```bash
sudo systemctl stop testpress-worker
```

- Stops the currently running service.
- Does not remove its automatic startup configuration.

### Disable

```bash
sudo systemctl disable testpress-worker
```

- Removes the automatic startup configuration.
- Does not necessarily stop a service that is already running.

### Stop and Disable Together

```bash
sudo systemctl disable --now testpress-worker
```

### Quick Comparison

| Command | Immediate Effect | Boot Effect |
|---|---|---|
| `start` | Starts service | No change |
| `stop` | Stops service | No change |
| `enable` | No immediate start by default | Starts at boot |
| `disable` | Does not necessarily stop | Removes automatic startup |
| `restart` | Restarts service | No change |

## 9. What is journalctl?

**journalctl** is the command-line utility used to read logs collected by the systemd journal.

It helps troubleshoot services and understand what happened when an application started, stopped or failed.

### Useful Commands

**View all logs from the service:**

```bash
journalctl -u testpress-worker
```

**View the last 20 log entries:**

```bash
journalctl -u testpress-worker -n 20
```

**Follow logs continuously:**

```bash
journalctl -u testpress-worker -f
```

**View logs from the current boot:**

```bash
journalctl -u testpress-worker -b
```

**View detailed service logs:**

```bash
sudo journalctl -xeu testpress-worker
```

**View logs without a pager:**

```bash
journalctl -u testpress-worker --no-pager
```

In this project, journalctl is used to verify heartbeat messages, service startup and graceful shutdown.

## 10. What is systemd-analyze verify?

The following command checks a service unit file for configuration errors:

```bash
sudo systemd-analyze verify /etc/systemd/system/testpress-worker.service
```

It helps identify invalid directives and other configuration problems.

To display the directories systemd searches for unit files, execute:

```bash
systemd-analyze unit-paths
```

## 11. How Does the Python Worker Work?

The application is deployed at:

```text
/opt/testpress-worker/app.py
```

The systemd configuration is located at:

```text
/etc/systemd/system/testpress-worker.service
```

### Service Configuration

```ini
[Unit]
Description=Testpress Python Background Worker
After=network.target

[Service]
Type=simple
User=labuser
Group=labuser
WorkingDirectory=/opt/testpress-worker
EnvironmentFile=/etc/testpress-worker/worker.env
ExecStart=/usr/bin/python3 /opt/testpress-worker/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Execution Flow

1. Linux boots.
2. systemd starts managing the system services.
3. systemd checks which services are enabled.
4. The `testpress-worker` service is enabled.
5. systemd reads its service configuration.
6. systemd executes the Python application using `/usr/bin/python3`.
7. The application runs under the configured `labuser` account, not root.
8. The application continuously writes heartbeat messages.
9. If the application crashes, systemd attempts to restart it according to the configured restart policy.

## 12. Process Termination and Restart Behaviour

Two termination scenarios were tested.

### Scenario 1: Graceful Termination

Execute:

```bash
sudo kill -SIGTERM <PID>
```

The Python application receives signal 15 (SIGTERM).

The application handles the signal and performs a graceful shutdown.

Example log output:

```text
Received signal 15. Shutting down gracefully.
Worker shutdown complete.
```

With `Restart=always`, systemd can restart the process even after a successful exit. Restart behaviour also depends on how the service was stopped.

### Scenario 2: Forced Termination

Execute:

```bash
sudo kill -9 <PID>
```

SIGKILL immediately terminates the process.

The Python application cannot handle this signal or perform its graceful shutdown routine.

systemd detects that the main process has been killed and restarts it according to:

```ini
Restart=always
RestartSec=5
```

A new process starts with a different PID.

## 13. Automatic Startup After Reboot

Enable the service:

```bash
sudo systemctl enable testpress-worker
```

Reboot Linux:

```bash
sudo reboot
```

After logging in again, check the service status:

```bash
sudo systemctl status testpress-worker
```

Verify automatic startup and process execution:

```bash
systemctl is-enabled testpress-worker
systemctl is-active testpress-worker
pgrep -af app.py
```

### Expected Results

```text
enabled
active
443 /usr/bin/python3 /opt/testpress-worker/app.py
```

The PID may change after every reboot.

These checks confirm that the worker starts automatically after reboot.

## 14. Final Project Verification

Execute the following commands to verify the entire setup:

```bash
echo "===== SERVICE STATUS ====="
systemctl is-active testpress-worker

echo "===== BOOT ENABLEMENT ====="
systemctl is-enabled testpress-worker

echo "===== RUNNING PROCESS ====="
pgrep -af app.py

echo "===== SERVICE DETAILS ====="
sudo systemctl status testpress-worker

echo "===== RECENT LOGS ====="
journalctl -u testpress-worker -n 10 --no-pager
```

## 15. What This Project Covers

This project demonstrates practical knowledge of:

- Linux process management.
- Background processes and daemons.
- systemd and systemctl.
- systemd unit files and their locations.
- Application deployment under `/opt`.
- Environment variable management using environment files.
- Running applications under a dedicated Linux user.
- Starting and stopping Linux services.
- Enabling services at boot.
- Restart policies and automatic recovery.
- Graceful shutdown using SIGTERM.
- Forced termination using SIGKILL.
- Monitoring logs using journalctl.
- Validating service configuration.
- Testing service persistence across system reboots.

## 16. Project Structure

```text
linux-process-mangement/
│
├── app.py
├── worker.env
├── testpress-worker.service
├── learn.md
├── README.md
│
└── evidence/
    ├── 01-running-process.png
    ├── 02-graceful-shutdown.png
    ├── 03-forced-termination.png
    ├── 04-automatic-restart.png
    └── 05-enabled-at-boot.png
```

## 17. Conclusion

This project demonstrates how to deploy a Python application as a Linux-managed background service using systemd.

It covers service configuration, process management, automatic startup, restart policies, graceful termination and centralized log monitoring.

The result is a Python worker that can operate independently of an interactive terminal session and be managed through standard Linux service management commands.
