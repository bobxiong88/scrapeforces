import sys
input = sys.stdin.readline
for _ in range(int(input())):
    s = input().strip('\n')
    t = input().strip('\n')
    i = len(s)-1
    ans = "YES"
    j = len(t)-1
    while j >= 0:
        if i < 0:
            ans = "NO"
            break
        if s[i] == t[j]:
            i -= 1
            j -= 1
        else:
            i -= 2
    print(ans)
        
