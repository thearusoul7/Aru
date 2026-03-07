n = int(input())
words = input().split()

for i, word in enumerate(words):
    print(i, word, sep=":", end=" ")
