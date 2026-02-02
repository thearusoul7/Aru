
a = int(input())
n = list(map(int,input().split()))
maxx = max(n)

for i in range(a):
    if n[i] == maxx:
        print(i+1)