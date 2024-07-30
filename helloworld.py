def std_weight(height, gender):
    if gender == "남자":
        return height * height * 22
    else:
        return height * height * 21


height = 181
gender = "남자"
weight = std_weight(height / 100, gender)
print(f"키 {height} {gender}의 표준 체중: {weight}")
