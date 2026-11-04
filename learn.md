Linux Process Management – Running a Python Worker with systemd
1. What I Learned

In this project, I learned how to run a Python application as a Linux background service using systemd.

Instead of manually executing a Python script from the terminal, I configured Linux to manage the application as a service.

The service can:

Run in the background without keeping a terminal open.
Start automatically when the system boots.
Restart automatically if the application crashes.
Stop gracefully when it receives a termination signal.
Maintain logs that can be inspected later.
Run under a dedicated, non-root Linux user.
2. What is systemd?

systemd is the system and service manager used by many Linux distributions, including Ubuntu.

It is responsible for managing system services and other processes during system startup and normal operation.

Examples of services managed by systemd:

SSH server
Cron service
Docker service
Network services
Custom Python background workers

In this project: systemd manages my testpress-worker Python application.

3. What is systemctl?

systemctl is the command-line utility used to communicate with systemd.

We use it to start, stop, restart, enable, disable and inspect services.

Common commands:

Command	Purpose
sudo systemctl start SERVICE	Start a service
sudo systemctl stop SERVICE	Stop a service
sudo systemctl restart SERVICE	Restart a service
sudo systemctl status SERVICE	Check service status
sudo systemctl enable SERVICE	Enable automatic startup at boot
sudo systemctl disable SERVICE	Disable automatic startup at boot
systemctl is-active SERVICE	Check whether service is active
systemctl is-enabled SERVICE	Check whether service is enabled
sudo systemctl daemon-reload	Reload systemd unit definitions
4. What is a daemon?

A daemon is a background process that runs without requiring an interactive terminal session.

Examples:

sshd – SSH server daemon
cron – Scheduled task daemon
systemd-journald – Logging service
Our Python worker – A background application process

Important distinction:

A daemon is a background process.
systemd is a service manager that can manage daemons.
systemctl is the command-line tool used to control systemd.

Not every background process is necessarily managed by systemd.

5. Where should systemd service files be located?

To understand where systemd searches for unit files, use:

bash
systemd-analyze unit-paths


This displays the directories systemd searches for unit files.

Important locations:

Directory	Purpose
/etc/systemd/system/	Administrator-created services and local overrides
/run/systemd/system/	Runtime unit files
/usr/lib/systemd/system/	System and package-provided unit files on many distributions
/lib/systemd/system/	Package-provided unit files on some distributions

For our custom application, we created:

text
/etc/systemd/system/testpress-worker.service


This is the recommended location for a system-wide custom service.

Note: The exact unit search paths vary between Linux distributions.

6. Why are app.py and the service file in different locations?

Our project has two important locations:

Application location:

text
/opt/testpress-worker/app.py


Systemd service configuration:

text
/etc/systemd/system/testpress-worker.service


Why?

The application and its service configuration have different responsibilities.

Location	Responsibility
/opt/testpress-worker/	Stores the deployed application
/etc/systemd/system/	Stores instructions for systemd about how to manage the application

The service file tells systemd:

Which user should execute the application.
Which working directory to use.
Which Python interpreter to execute.
Where environment variables are stored.
How to restart the application.

We could technically execute the application directly from the Git repository.

However, keeping deployed applications under /opt separates application deployment from development files.

This makes the deployment easier to manage.

7. Difference Between start and enable

These two commands perform different operations.

Start:

bash
sudo systemctl start testpress-worker


Starts the service immediately.

It does not automatically configure the service to start after a reboot.

Enable:

bash
sudo systemctl enable testpress-worker


Configures the service to start automatically during the appropriate system boot target.

It does not necessarily start the service immediately.

To do both:

bash
sudo systemctl enable --now testpress-worker

8. Difference Between stop and disable

Stop:

bash
sudo systemctl stop testpress-worker


Stops the currently running service.

It does not remove its automatic startup configuration.

Disable:

bash
sudo systemctl disable testpress-worker


Removes the automatic startup configuration.

It does not necessarily stop a service that is already running.

To disable and stop:

bash
sudo systemctl disable --now testpress-worker

Quick comparison
Command	Immediate effect	Boot effect
start	Starts service	No change
stop	Stops service	No change
enable	No immediate start by default	Starts at boot
disable	Does not necessarily stop	Removes automatic startup
restart	Restarts service	No change
9. What is journalctl?

journalctl is the command-line utility used to read logs collected by the systemd journal.

It helps us troubleshoot services and understand what happened when an application started, stopped or failed.

Useful commands:

bash
# View all logs from our service
journalctl -u testpress-worker

# View the last 20 log entries
journalctl -u testpress-worker -n 20

# Follow logs continuously
journalctl -u testpress-worker -f

# View logs from the current boot
journalctl -u testpress-worker -b

# View detailed service logs
sudo journalctl -xeu testpress-worker

# View logs without a pager
journalctl -u testpress-worker --no-pager


In our project, journalctl helped us verify the Python worker's heartbeat messages and graceful shutdown.

10. What is systemd-analyze verify?

We used:

bash
sudo systemd-analyze verify /etc/systemd/system/testpress-worker.service


This checks a service unit file for configuration errors.

It helps identify invalid directives and other configuration problems.

We also used:

bash
systemd-analyze unit-paths


This displays the directories systemd searches for unit files.

11. How does our Python worker work?

Our application is deployed at:

text
/opt/testpress-worker/app.py


The systemd configuration is:

text
/etc/systemd/system/testpress-worker.service


The service configuration contains:

ini
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

How the execution happens
Linux boots.
systemd starts managing the system services.
systemd checks which services are enabled.
Our testpress-worker service is enabled.
systemd reads its service configuration.
systemd executes the Python application using /usr/bin/python3.
The application runs as labuser, not root.
The application continuously writes heartbeat messages.
If the application crashes, systemd attempts to restart it according to the restart policy.
12. What happens when we terminate the process?

We tested two scenarios.

Scenario 1: Graceful termination
bash
sudo kill -SIGTERM 5931


The Python application receives signal 15 (SIGTERM).

It handles the signal and performs a graceful shutdown.

The logs showed:

text
Received signal 15. Shutting down gracefully.
Worker shutdown complete.


The service became inactive.

Scenario 2: Forced termination
bash
sudo kill -9 7479


SIGKILL immediately terminates the process.

The Python application cannot handle this signal or perform its graceful shutdown routine.

systemd detects that the process has failed and restarts it according to:

ini
Restart=always
RestartSec=5


We verified that a new process started with a different PID.

13. How did we verify automatic startup after reboot?

We enabled the service:

bash
sudo systemctl enable testpress-worker


Then rebooted Linux:

bash
sudo reboot


After logging in again, we checked:

bash
sudo systemctl status testpress-worker


We also verified:

bash
systemctl is-enabled testpress-worker
systemctl is-active testpress-worker
pgrep -af app.py


Expected results:

text
enabled
active
443 /usr/bin/python3 /opt/testpress-worker/app.py


The PID may change after every reboot.

This confirmed that our worker started automatically after reboot.

14. Final Project Verification

The following commands can be used to verify the entire setup:

bash
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

15. Key Takeaways

Through this project, I learned:

Linux process management.
Background processes and daemons.
systemd and systemctl.
systemd unit files and their locations.
Deploying applications under /opt.
Managing environment variables using environment files.
Running applications under a dedicated Linux user.
Starting and stopping Linux services.
Enabling services at boot.
Restart policies and automatic recovery.
Graceful shutdown using SIGTERM.
Forced termination using SIGKILL.
Monitoring logs using journalctl.
Validating service configuration.
Testing service persistence across system reboots.

Final learning: Instead of manually running a Python application from a terminal, I now understand how to deploy it as a Linux-managed background service that can start automatically, run continuously and recover from unexpected process termination.