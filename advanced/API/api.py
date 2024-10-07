import numpy as np
import pandas as pd
import psycopg2
import requests
import urllib
import json
from urllib.parse import urlencode, unquote, quote_plus
from urllib.request import urlopen
import datetime as datetime

from DB import db
import params as pa

Key = '70f9dc14be4a4107bcd0af657ecc92ec'
HourlyPresent = '/current'
BasicUrl = 'https://api.weatherbit.io/v2.0'


def CurrentCollector():
    LAT = 34
    LNG = 125.74115

    params = '?' + urlencode(
        {
            quote_plus("lat"): str(LAT),
            quote_plus("lon"): str(LNG),
            quote_plus("key"): Key,
            quote_plus("include"): 'minutely'
        })

    FinalURL = BasicUrl + HourlyPresent + unquote(params)
    req = urllib.request.Request(FinalURL)

    response_body = urlopen(req).read()
    data = json.loads(response_body)

    DF = pd.DataFrame.from_dict(data['data'])
    del DF['ts']

    DF2 = DF[['lon', 'lat', 'temp', 'dewpt']]

    PreNow = datetime.datetime.today()
    PreNow = PreNow.replace(second=0, minute=0, microsecond=0)
    DF2 = DF2.assign(target=PreNow)

    print(DF2)

    # Bring DB
    conn = psycopg2.connect(host=pa.host, dbname=pa.dbname, user=pa.user, password=pa.password, port=pa.port)
    cur = conn.cursor()

    Target = DF2.loc[0, 'target']
    LAT = DF2.loc[0, 'lat']
    LON = DF2.loc[0, 'lon']
    Temp = DF2.loc[0, 'temp']
    Dew = DF2.loc[0, 'dewpt']

    select_all_sql = (f"select EXISTS(select * from weather "
                      f"where target = TIMESTAMP '%s' AND lat = %s AND lon = %s)" % (Target, LAT, LON))

    cur.execute(select_all_sql)
    Exists = cur.fetchone()[0]

    if not Exists:
        print("Upload: ", Target, Temp, Dew)
        query = (""" INSERT INTO weather (target,lat,lon,temp,dewpt)
         values (TIMESTAMP '%s',%s,%s,%s,%s) """ % (Target, LAT, LON, Temp, Dew))
        cur.execute(query)

    else:
        print("Duplicated ", Target, Temp, Dew)
        query = (""" UPDATE weather SET temp = %s and dewpt= %s where target = TIMESTAMP '%s'
         AND lat = %s AND lon=%s """ % (Temp, Dew, Target, LAT, LON))
        cur.execute(query)

    conn.commit()
    cur.close()
    conn.close()

    return DF2


if __name__ == '__main__':
    CurrentCollector()
