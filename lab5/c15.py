#a1b2c3
#out: a11b22c33
import re
def func(g):
    d=g.group()
    return d*2
a=input()
print(re.sub(r"\d",func,a))