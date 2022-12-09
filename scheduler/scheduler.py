import time
import atexit

import schedule
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


# schedulers
def print_time():
    print(time.strftime('%H:%M:%S'))


scheduler = BackgroundScheduler()
trigger = CronTrigger(day_of_week='mon-fri')
trigger_one = CronTrigger(second='15')
scheduler.start()
scheduler.add_job(print_time,
                  trigger=trigger)
atexit.register(lambda: scheduler.shutdown())


# schedule.every()