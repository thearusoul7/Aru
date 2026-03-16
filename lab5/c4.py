#input: abc123xyz
#output: 1 2 3
import re
a=input()
b = re.findall("[0-9]", a)
for i in b:
    print(i, end=" ")

