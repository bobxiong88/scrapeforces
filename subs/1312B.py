import sys
input = sys.stdin.readline
for _ in range(int(input())):
    n = int(input())
    a = list(map(int,input().split()))
    print(*reversed(sorted(a)))
