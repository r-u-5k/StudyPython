import json
import urllib
from urllib.parse import urlencode, unquote, quote_plus
from urllib.request import urlopen

import pandas as pd

import params as pa
from DB import db_new

BasicUrl = 'http://apis.data.go.kr/1360000/NwpModelInfoService/getLdapsUnisArea'

pd.set_option("display.width", 5000)
pd.set_option("display.max_rows", 5000)
pd.set_option("display.max_columns", 5000)


def ldaps(DongCode):
    params = '?' + urlencode(
        {
            quote_plus("serviceKey"): pa.Key,
            quote_plus("numOfRows"): str(100),
            quote_plus("pageNo"): str(1),
            quote_plus("dataType"): "JSON",
            quote_plus("baseTime"): str(202410100300),
            quote_plus("dongCode"): str(DongCode),
            quote_plus("dataTypeCd"): "Temp",
        })

    # http://apis.data.go.kr/1360000/NwpModelInfoService/getLdapsUnisArea
    # ?serviceKey=인증키&numOfRows=10&pageNo=1
    # &baseTime=201911120300&dongCode=1100000000&dataTypeCd=Temp

    FinalURL = BasicUrl + unquote(params)
    req = urllib.request.Request(FinalURL)

    response_body = urlopen(req).read()
    data = json.loads(response_body)

    items = data['response']['body']['items']['item']

    df = pd.DataFrame(items)
    df["baseTime"] = pd.to_datetime(df["baseTime"], format="%Y%m%d%H%M")
    df["fcstTime"] = pd.to_datetime(df["fcstTime"], format="%Y%m%d%H%M")
    df = df.rename(columns={"baseTime": "basetime", "fcstTime": "fcsttime", "value": "temp"})
    df = df.astype({"lon": "float"})
    df = df.astype({"lat": "float"})
    del df["unit"]

    return df


if __name__ == '__main__':
    Temp = ldaps(1153059500)
    db_new.DirectUpload('temp.csv', 'ldaps', Temp, ['basetime', 'fcsttime', 'lon', 'lat', 'temp'])
