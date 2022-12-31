import requests
import json
import bs4
import csv
import time
import os
path = "C:\\Users\\Admin\\Desktop\\Scrapeforces\\bobxiong88\\"
handle = "bobxiong88"
handleurl = "https://codeforces.com/api/user.status?handle={}&from=1&count=10000".format(handle)
response = requests.get(handleurl)
submissions = json.loads(response.text)['result']
exist = set([i[:i.index('.')] for i in os.listdir(path)])
print(exist)
time.sleep(1)
for submission in submissions:
    if submission['verdict'] != 'OK': continue
    contestId = submission['contestId']
    submissionId = submission['id']
    problemId = submission['problem']['index']
    fname = str(contestId)+problemId
    if str(contestId) in [str(i) for i in [101021, 103037, 102365]]: continue
    if fname in exist: continue
    print("__________________________________________________________")
    print("Processing... {}".format(fname))
    suburl = "https://codeforces.com/contest/{}/submission/{}".format(contestId,submissionId)
    print(suburl)
    cnt = 0
    while True:
        try:
            cnt += 1
            response = requests.get(suburl)
            sub = response.text
            content = bs4.BeautifulSoup(sub, "html.parser")
            codecont = content.find_all("pre", {"id": "program-source-text"})[0]
            break
        except:
            print("Failed!")
            if cnt > 1:
                break
            print("Trying again in 30 seconds")
            time.sleep(30)
    if cnt > 1:
        print("Skipping...")
        continue
    lang = codecont['class'][1][5:]
    code = codecont.getText()
    fname += "."+lang
    f = open(path+fname,"w")
    f.write(code)
    f.close()
    exist.add(fname)
    time.sleep(5)
