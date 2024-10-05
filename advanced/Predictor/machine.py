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
    FilePath = os.getenv("LOC")
    WeatherList = []
    FileList = os.listdir(FilePath)
    for file in FileList:
        if file.startswith("Weather"):
            FullFileName = os.path.join(FilePath, file)
            Weather = pd.read_csv(FullFileName)
            WeatherList.append(Weather)

    WeatherDF = pd.concat(WeatherList, ignore_index=True)
    WeatherDF["DeliveryDT"] = pd.to_datetime(WeatherDF["DeliveryDT"])
    del WeatherDF["WeatherType"]
    WeatherDF = WeatherDF.sort_values(by="DeliveryDT", ascending=[True])
    return WeatherDF


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

    return pred, Machine


def testing(TestingData, Machine):
    TestingData.index = range(0, len(TestingData))
    Y_test = TestingData["Target"].copy()
    X_test = TestingData.copy()
    del X_test["Target"]
    del X_test["DeliveryDT"]
    del X_test["WeatherStationId"]

    pred = Machine.predict(X_test)
    pred = np.round(pred, 2)

    plt.figure(1)
    plt.plot(TestingData.loc[24:47, 'DeliveryDT'], Y_test[24:48], label="Actual")
    plt.plot(TestingData.loc[24:47, 'DeliveryDT'], pred[24:48], label="Prediction")
    plt.legend()
    plt.grid(True)
    plt.draw()
    plt.interactive(False)
    plt.show()

    return pred


def performance(Method, Pred, Actual):
    if Method == "MAPE":
        Error = abs(Pred - Actual) / Actual
        Inf = np.where(Error == np.inf)[0]
        Error.loc[Inf] = 0
        Accuracy = round(np.mean(Error) * 100, 2)

    elif Method == "MAPE_Solar":
        Error = abs(Pred - Actual) / Actual
        Inf = np.where(Error == np.inf)[0]
        Error[Inf] = 0

        Small = np.where(Actual < 1000)[0]
        Error[Small] = 0

        NoZero = np.where(Error > 0)[0]
        RealError = Error[NoZero]
        Accuracy = round(np.mean(RealError) * 100, 2)

    elif Method == "RMSE":
        SE = abs(Pred - Actual) * abs(Pred - Actual)
        MSE = np.mean(SE)
        Accuracy = np.sqrt(MSE)

    Accuracy = np.round(Accuracy, 2)
    return Accuracy


if __name__ == "__main__":
    TrainingStart = pd.Timestamp(year=2022, month=1, day=1, hour=0)
    TrainingEnd = pd.Timestamp(year=2022, month=12, day=31, hour=23)
    TestingStart = pd.Timestamp(year=2023, month=1, day=1, hour=0)
    TestingEnd = pd.Timestamp(year=2023, month=6, day=30, hour=23)

    Solar = solar_read()
    Weather = weather_read()
    TotalData = pd.merge(Solar, Weather, how='inner', on='DeliveryDT')
    TrainingData = TotalData[(TotalData['DeliveryDT'] >= TrainingStart) & (TotalData['DeliveryDT'] <= TrainingEnd)]
    Output, FitMachine = training(TrainingData)

    TrainingAccuracy = performance('MAPE_Solar', Output, TrainingData.Target.to_numpy())

    TestingData = TotalData[(TotalData['DeliveryDT'] >= TestingStart) & (TotalData['DeliveryDT'] <= TestingEnd)]
    Forecast = testing(TestingData, FitMachine)
    TestingAccuracy = performance('MAPE_Solar', Forecast, TestingData.Target.to_numpy())
