import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import params as pa
import numpy as np
import random

from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

StartPath = os.getcwd()
os.chdir('..')
Source = os.getcwd()
sys.path.append(Source)
load_dotenv(dotenv_path=os.path.join(Source, '.env'))
os.chdir(StartPath)

pd.set_option("display.width", 5000)
pd.set_option("display.max_rows", 5000)
pd.set_option("display.max_columns", 5000)


def solar_read():
    FilePath = os.path.join(pa.Loc, pa.FileNameSolar)
    Solar = pd.read_csv(FilePath)
    Solar["DeliveryDT"] = pd.to_datetime(Solar["DeliveryDT"])
    Solar = Solar.sort_values(by="DeliveryDT", ascending=[True])
    Solar = Solar.rename(columns={'MW': "Target"})
    return Solar


def weather_read():
    FilePath = os.path.join(pa.Loc, pa.FileNameWeather)
    Weather = pd.read_csv(FilePath)
    Weather["DeliveryDT"] = pd.to_datetime(Weather["DeliveryDT"])
    del Weather['WeatherType']
    Weather = Weather.sort_values(by="DeliveryDT", ascending=[True])
    return Weather


def regression():
    if pa.Machine == "RF":
        machine = RandomForestRegressor(
            n_estimators=pa.RF_Tree,
            criterion="squared_error",
            max_depth=pa.RF_Depth,
            min_samples_split=pa.RF_MinLeaf * 2,
            min_samples_leaf=pa.RF_MinLeaf,
            n_jobs=pa.RF_njob,
            max_features=pa.RFMF,  # 'sqrt' auto None 1.0
            max_samples=pa.max_samples,  # 1.0, # 0.5, # 0.5 None
            bootstrap=True,
            random_state=random.randint(0, 1000),
            verbose=0,
        )

    elif pa.Machine == "GBM":
        machine = GradientBoostingRegressor(
            n_estimators=pa.GBM_Tree,
            learning_rate=pa.GBM_LR,
            max_depth=pa.GBM_Depth,
            random_state=random.randint(0, 1000),
            criterion="friedman_mse",
            subsample=pa.subsample,
            min_samples_split=2,
            max_features=pa.GBMMF,  # sqrt auto
            verbose=0,
            loss="squared_error",
        )

    elif pa.Machine == "LR":
        machine = LinearRegression(fit_intercept=True)

    return machine


def training(TrainingData):
    Y_train = TrainingData["Target"].copy()
    X_train = TrainingData.copy()
    del X_train["Target"]
    del X_train["DeliveryDT"]
    del X_train["WeatherStationId"]

    Machine = regression()
    Machine.fit(X_train, Y_train)

    pred = Machine.predict(X_train)
    pred = np.round(pred, 2)

    plt.figure(1)
    plt.plot(TrainingData['DeliveryDT'], Y_train, label="Actual")
    plt.plot(TrainingData['DeliveryDT'], pred, label="Prediction")
    plt.legend()
    plt.grid(True)
    plt.draw()
    plt.interactive(False)
    # plt.show(block=False)
    plt.show()

    return pred


if __name__ == "__main__":
    Solar = solar_read()
    Weather = weather_read()
    TrainingData = pd.merge(Solar, Weather, how='inner', on='DeliveryDT')
    Output = training(TrainingData)
