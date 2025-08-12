from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .runner import run_once


def main():
    sched = BlockingScheduler(timezone="US/Eastern")
    trig = CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*/10")
    sched.add_job(run_once, trig, id="sell-decision")
    sched.start()


if __name__ == "__main__":  # pragma: no cover
    main()
