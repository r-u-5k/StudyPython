import os

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

import params as pa

conn_string = 'postgresql://' + pa.user + ":" + pa.password + "@" + pa.host + ":" + str(pa.port) + "/" + pa.dbname


def DirectUpload(FullPath, Table, Data, Columns):
    conn = psycopg2.connect(host=pa.host, dbname=pa.dbname, user=pa.user, password=pa.password, port=pa.port)
    cur = conn.cursor()

    drop_query = f"DROP TABLE IF EXISTS {Table};"
    cur.execute(drop_query)

    create_query = f"""
    CREATE TABLE {Table} (
        basetime TIMESTAMP,
        fcsttime TIMESTAMP,
        lon DOUBLE PRECISION,
        lat DOUBLE PRECISION,
        temp DOUBLE PRECISION
    );
    """
    cur.execute(create_query)

    Data.to_csv(FullPath, index=False, header=False)
    f = open(FullPath, 'r')
    cur.copy_from(f, Table, sep=',', columns=Columns)
    f.close()

    # Remove
    os.remove(FullPath)

    conn.commit()
    cur.close()
    conn.close()

    return []
