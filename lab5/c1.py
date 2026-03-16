#input: Hello world
import re
a = input()

if re.match("Hello", a):
    print("YES")
else:
    print("NO")