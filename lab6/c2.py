a = int(input())
n = list(map(int, input().split()))
c = len(list(filter(lambda x: x % 2 == 0, n)))

print(c)