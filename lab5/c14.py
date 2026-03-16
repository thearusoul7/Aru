#1234
#Match
import re
a = input()
b = re.compile(r'^\d+$')
if b.fullmatch(a):
    print("Match")
else:
    print("No match")
