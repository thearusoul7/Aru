a = int(input())
n = list(map(int,input().split()))
n.sort(reverse = True)
print(*n)