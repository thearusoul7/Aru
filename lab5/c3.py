#input: hello hello hello
#       hello 
#       3
import re
a = input()
b = input()
c = 0
for i in re.findall(b, a):
    c+=1
print(c)