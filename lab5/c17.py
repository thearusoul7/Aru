#Today is 12/05/2023 and tomorrow is 13/05/2023
# 2
import re
s = input()
dates = re.findall(r'\d{2}/\d{2}/\d{4}', s)
print(len(dates))