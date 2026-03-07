a = int(input())
n = list(map(int,input().split()))
c = 0
for i in n:
    i = i ** 2
    c += i
print(c)