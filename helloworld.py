url = "http://naver.com"
my_str = url.replace("http://", "")
my_str = my_str[0 : my_str.index(".")]
password = my_str[0:3] + str(len(my_str)) + str(my_str.count("e")) + "!"
print(f"{url}의 비밀번호는 {password}입니다.")
