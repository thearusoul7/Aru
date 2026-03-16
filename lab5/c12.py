#abc12dh34h5
#out:12 34
import re
a = input()
x = re.findall(r'\d{2,}', a)
if x:
    print(*x)
else:
    print(" ")