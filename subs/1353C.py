import sys
input = sys.stdin.readline
t = int(input())
for _ in range(t):
    n = int(input())
    ans = 0
    for i in range(n//2+1):
        ans+=i*4*2*i
    print(ans)
