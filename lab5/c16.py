#Name: Bob, Age: 31
#Bob 31
import re
s = input()
match = re.search(r'Name: (.*), Age: (\d+)', s)
print(match.group(1), match.group(2))