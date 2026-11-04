
import logging
import os
import signal
import sys
import time
from threading import Event

stop_event = Event()

HEARTBEAT_INTERVAL = float(
    os.getenv("HEARTBEAT_INTERVAL", "5")
)
CRASH_AFTER_SECONDS = int(
    os.getenv("CRASH_AFTER_SECONDS", "0")
)
MEMORY_HOG_MB = int(
    os.getenv("MEMORY_HOG_MB", "0")
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("testpress-worker")


def handle_shutdown(signum, frame):
    logger.info("Received signal %s. Shutting down gracefully.", signum)
    stop_event.set()


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def consume_memory():
    blocks = []
    logger.info("Starting memory test: %s MB", MEMORY_HOG_MB)

    for i in range(MEMORY_HOG_MB):
        blocks.append(bytearray(1024 * 1024))
        if (i + 1) % 10 == 0:
            logger.info("Allocated %s MB", i + 1)
        time.sleep(0.05)

    logger.info("Memory allocation completed: %s MB", MEMORY_HOG_MB)

    while not stop_event.wait(1):
        pass


def main():
    start_time = time.monotonic()
    pid = os.getpid()

    logger.info("Testpress worker started. PID=%s", pid)
    logger.info("Heartbeat interval: %s seconds", HEARTBEAT_INTERVAL)

    try:
        if MEMORY_HOG_MB > 0:
            consume_memory()
            return

        while not stop_event.is_set():
            elapsed = time.monotonic() - start_time

            if CRASH_AFTER_SECONDS > 0 and elapsed >= CRASH_AFTER_SECONDS:
                logger.error("Simulated application crash!")
                sys.exit(1)

            logger.info("Heartbeat: worker alive. PID=%s", pid)

            stop_event.wait(HEARTBEAT_INTERVAL)

    finally:
        logger.info("Worker shutdown complete.")


if __name__ == "__main__":
    main()
