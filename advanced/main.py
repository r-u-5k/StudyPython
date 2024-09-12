import test as tt
import pandas as pd


if __name__ == "__main__":
    tt.new_response()

Dist = pd.DataFrame(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                    columns=['A', 'B', 'C'],
                    index=['X', 'Y', 'Z'])
print(Dist)
print(Dist.index)
print(Dist.columns)
print(Dist['A'])

A = """
여러
줄에
걸친
문자열
"""
print(A)

B = """이스케이프 문자 없이 "큰따옴표" 사용 가능"""
print(B)
