#hello world , world , Python
#out:hello Python
import re
a = input()
b = input()
v = input()
c = re.sub(b, v, a)
print(c)