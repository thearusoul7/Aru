#I have a cat
#Yes
import re
a = input()
if re.findall(r"cat|dog", a):
    print("Yes")
else:
    print("No")