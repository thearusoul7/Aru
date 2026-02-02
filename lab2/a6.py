a = int(input())
b = input().split()
s = int(b[0])
for i in b[1:]:
    if int(i) > s:
        s = int(i)
print(s)