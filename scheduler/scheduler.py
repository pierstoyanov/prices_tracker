# import time
# import atexit
# import schedule
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from apscheduler.triggers.interval import IntervalTrigger
# from logger.logger import logging

# # looger
# sch_log = logging.getLogger('scheduler')

#
# # schedulers
# def print_time():
#     print(time.strftime('%H:%M:%S'))
#
#
# def send_daly_msg(viber, users, msg):
#     for u in users:
#         token = viber.send_messages(u, msg)
#         sch_log.info(token)


# scheduler = BackgroundScheduler()
# trigger = CronTrigger(hour=16, minute=30, day_of_week='mon-fri')
# trigger_one = CronTrigger(second='30')
# scheduler.start()

# # scheduler
# scheduler.add_job(lambda: data_management(),
#                             scheduler.trigger)
#
# scheduler.add_job(lambda: send_daly_msg(
#     viber, users, msg_text(daly)),
#     scheduler.trigger)

# atexit.register(lambda: scheduler.shutdown())
