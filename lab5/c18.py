#a.b.c.d
#.
#out:3
import re

s = input()
p = input()

a = re.escape(p)
b = re.findall(a, s)
print(len(b))