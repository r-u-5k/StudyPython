import sys

import params as pa
import pandas as pd
import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import cr

pd.set_option('display.width', 5000)
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)


def mycrawl(dti):
    Farm = 1
    TargetDay = dti[pa.rotation]
    Data = cr.GetGenData(TargetDay.strftime("%Y-%m-%d"), Farm)
    pa.rotation += 1
    return Data


if __name__ == "__main__":
    arg = sys.argv[1:]
    if len(arg) > 0:
        print(arg[0])
        StartDay = arg[0]
        EndDay = arg[2]
    else:
        StartDay = '2024-09-01'
        EndDay = '2024-09-30'

    sched = BackgroundScheduler(timezone="Asia/Seoul")

    dti = pd.date_range(start=StartDay, end=EndDay, freq="1D")
    mycrawl(dti)

    sched.add_job(mycrawl, 'interval', minutes=3, id="Solar", args=[dti], max_instances=1)
    sched.start()

    while True:
        Now = datetime.datetime.today().replace(second=0, microsecond=0)
        print(dti[pa.rotation], Now)
        time.sleep(10)
