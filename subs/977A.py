import sys
input = sys.stdin.readline

n, k = map(int,input().split())
for i in range(k):
    if str(n)[-1]!='0':
        n-=1
    else:
        n = int(n/10)
print(n)
