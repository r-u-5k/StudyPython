from pandas import Series


data = [100, 200, 300]
index = ["월", "화", "수"]
s = Series(data, index)

print(s.iloc[0:2])
print(s.loc["월":"화"])
# 월    100
# 화    200

print(s.iloc[[0, 2]])
print(s.loc[["월", "수"]])
# 월    100
# 수    300
