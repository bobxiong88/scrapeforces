import sys
input = sys.stdin.readline
for _ in range(int(input())):
    a, b = map(int,input().split())
    if a == b:
        print(0,0)
        continue
    a, b = sorted([a, b])
    k = b-a
    print(k, min(b%k, k-b%k,a))
    
