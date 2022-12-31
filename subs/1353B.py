import sys
input = sys.stdin.readline
t = int(input())
for _ in range(t):
    n,k = map(int,input().split())
    A = list(map(int,input().split()))
    B = list(map(int,input().split()))
    for _ in range(k):
        b,bi = -1,-1
        s,si = float('inf'),-1
        for i in range(n):
            if A[i]<s:
                s = A[i]
                si = i
            if B[i]>b:
                b = B[i]
                bi = i
        if b>s:
            A[si]=b
            B[bi]=s
    print(sum(A))
