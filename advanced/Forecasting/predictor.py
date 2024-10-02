import pandas as pd
import numpy as np
import os

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

def DataReader(Loc, FileName):
    Path = os.path.join(Loc, FileName)
    TempWeather = pd.read_csv(Path)
    TempWeather["DeliveryDT"] = pd.to_datetime(TempWeather["DeliveryDT"],
                                               format='%Y-%m-%d %H:%M:%S',
                                               utc=False)
    return TempWeather


# def trainer():
#
#     File = "RenewableHist.csv"
#     Solar = pr.