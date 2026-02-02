
a = int(input())
n = list(map(int,input().split()))
maxx = max(n)
minn = min(n)

for i in range(a):
    if n[i] == maxx:
        n[i] = minn
print(*n)