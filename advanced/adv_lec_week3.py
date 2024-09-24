import numpy as np
import pandas as pd

Solar = pd.read_csv('C:/Users/Jin/OneDrive/학교/강의자료/전기전자심화설계/Data1/Solar_4.csv')

Solar['DeliveryDT'] = pd.to_datetime(Solar['DeliveryDT'])

print(Solar)
