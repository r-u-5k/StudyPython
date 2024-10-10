import os
import random
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, TimeSeriesSplit, GridSearchCV

import params as pa

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
    return RandomForestRegressor(
        n_estimators=pa.RF_Tree,
        criterion="squared_error",
        max_depth=pa.RF_Depth,
        min_samples_split=pa.RF_MinLeaf * 2,
        min_samples_leaf=pa.RF_MinLeaf,
        n_jobs=pa.RF_njob,
        max_features=pa.RFMF,
        max_samples=pa.max_samples,
        bootstrap=True,
        random_state=random.randint(0, 1000),
        verbose=0,
    )


def cross_validation(X, y, n_splits=5):
    model = regression()
    tscv = TimeSeriesSplit(n_splits=n_splits)

    # MAE 점수 계산 (음수 값으로 반환되므로 양수로 변환)
    mae_scores = -cross_val_score(model, X, y, cv=tscv, scoring='neg_mean_absolute_error')

    print("Cross-validation MAE scores:", mae_scores)
    print(f"Mean MAE: {np.mean(mae_scores):.2f} (+/- {np.std(mae_scores) * 2:.2f})")

    return np.mean(mae_scores)


def grid_search(X, y, n_splits=5):
    base_model = regression()

    # 기존 설정을 중심으로 탐색 범위 설정
    param_grid = {
        'n_estimators': [pa.RF_Tree//2, pa.RF_Tree, pa.RF_Tree*2],
        'max_depth': [pa.RF_Depth//2, pa.RF_Depth, pa.RF_Depth*2, None],
        'min_samples_split': [pa.RF_MinLeaf, pa.RF_MinLeaf*2, pa.RF_MinLeaf*4],
        'min_samples_leaf': [pa.RF_MinLeaf//2, pa.RF_MinLeaf, pa.RF_MinLeaf*2],
        'max_features': [pa.RFMF, 'sqrt', 'log2'],
        'max_samples': [pa.max_samples//2, pa.max_samples, pa.max_samples*2],
    }

    tscv = TimeSeriesSplit(n_splits=n_splits)

    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_absolute_error',
        n_jobs=pa.RF_njob,
        verbose=1
    )

    grid_search.fit(X, y)

    print("Best parameters found:", grid_search.best_params_)
    print(f"Best MAE: {-grid_search.best_score_:.2f}")

    return grid_search.best_estimator_, -grid_search.best_score_


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


def performance(Pred, Actual):
    Error = np.abs(np.divide(Pred - Actual, Actual, out=np.zeros_like(Actual), where=Actual != 0))

    Small = np.where(Actual < 1000)[0]
    Error[Small] = 0

    NoZero = np.where(Error > 0)[0]
    RealError = Error[NoZero]

    Accuracy = 100 - round(np.mean(RealError) * 100, 2)
    return Accuracy


if __name__ == "__main__":
    Solar = solar_read()
    Weather = weather_read()
    TotalData = pd.merge(Solar, Weather, how='inner', on='DeliveryDT')

    TrainingStart = pd.Timestamp(year=2022, month=1, day=1, hour=0)
    TrainingEnd = pd.Timestamp(year=2022, month=12, day=31, hour=23)
    TestingStart = pd.Timestamp(year=2023, month=1, day=1, hour=0)
    TestingEnd = pd.Timestamp(year=2023, month=6, day=30, hour=23)

    TrainingData = TotalData[(TotalData['DeliveryDT'] >= TrainingStart) & (TotalData['DeliveryDT'] <= TrainingEnd)]

    # Grid Search를 위한 데이터 준비
    X_train = TrainingData.drop(['Target', 'DeliveryDT', 'WeatherStationId'], axis=1)
    y_train = TrainingData['Target']

    # Grid Search 수행
    best_model, best_mae = grid_search(X_train, y_train)

    # 최적 모델로 예측
    train_pred = best_model.predict(X_train)
    TrainingAccuracy = performance(train_pred, y_train)

    TestingData = TotalData[(TotalData['DeliveryDT'] >= TestingStart) & (TotalData['DeliveryDT'] <= TestingEnd)]
    X_test = TestingData.drop(['Target', 'DeliveryDT', 'WeatherStationId'], axis=1)
    y_test = TestingData['Target']

    test_pred = best_model.predict(X_test)
    TestingAccuracy = performance(test_pred, y_test)

    print("\nResults Comparison:")
    print(f"Grid Search Best MAE: {best_mae:.2f}")
    print(f"Training Accuracy: {TrainingAccuracy:.2f}")
    print(f"Testing Accuracy: {TestingAccuracy:.2f}")

    # 기존 모델과 비교
    original_model = regression()
    original_model.fit(X_train, y_train)
    original_pred = original_model.predict(X_test)
    OriginalTestingAccuracy = performance(original_pred, y_test)
    print(f"Original Model Testing Accuracy: {OriginalTestingAccuracy:.2f}")
