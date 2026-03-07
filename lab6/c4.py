a = int(input())
b = list(map(int, input().split()))
c = list(map(int, input().split()))

s = 0
for i,g in zip(b, c):
    s += i * g

print(s)