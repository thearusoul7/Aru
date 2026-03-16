#input:Hello1
#output:Yes
import re
a = input()
if re.findall("^[A-Z]",a) or re.findall("^[a-z]", a) and re.findall("[0-9]$", a):
    print("Yes")
else:
    print("No")


