"""
Entry point — APScheduler polling loop.

Usage:
    pip install -r requirements.txt
    playwright install chromium
    cp .env.example .env   # fill in your keys
    python main.py

The agent logs into Dripify, polls the inbox every POLL_INTERVAL_MINUTES,
runs Emma on each new reply, and sends the response — fully automated.
"""
import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from config import settings
from agent import run_agent_cycle

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def main():
    log.info("Emma Sales Agent starting — poll every %d min", settings.poll_interval_minutes)

    scheduler = BlockingScheduler(timezone="Europe/Berlin")
    scheduler.add_job(
        run_agent_cycle,
        trigger="interval",
        minutes=settings.poll_interval_minutes,
        id="emma_poll",
        max_instances=1,
        misfire_grace_time=60,
    )

    # Run once immediately on startup
    log.info("Initial cycle...")
    run_agent_cycle()

    def _shutdown(signum, frame):
        log.info("Shutting down")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    scheduler.start()


if __name__ == "__main__":
    main()
