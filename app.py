from flask import Flask, render_template, redirect, request
from flask_executor import Executor
import json
from time import sleep
import bs4
import csv
import time
import os
import requests
import random

app = Flask(__name__)

executor = Executor(app)

@app.route("/start", methods = ['get'])
def post():
    handle = request.args.get('handle')
    status = request.args.get('status')
    unique = request.args.get('unique')
    executor.submit(get_submissions,handle,status,unique)
    return hash(handle+status+unique+str(random.randint(1,int(1e9)+7)))

@app.errorhandler(404)
def page_not_found(error):
    return "<h1> 404: Page not found <h1>"

def get_submissions(handle, status, unique):
    # in case people troll
    if not handle or not status or not unique: return

    # path to submission folder
    path = "submissions\\"

    # submission limit
    limit = 100

    # get submission ids
    handleurl = "https://codeforces.com/api/user.status?handle={}&from=1&count={}".format(handle, limit)
    response = requests.get(handleurl)
    submissions = json.loads(response.text)['result']

    # check for existing files
    exist = set([i[:i.index('.')] for i in os.listdir(path)])
    print(exist)

    # pause to not get rate limited by the cf server 
    time.sleep(1)

    # filter status
    if status != 'All':
        submissions = filter(lambda submission: submission['verdict'] == status, submissions)

    # uniqueness if required
    if unique == 'Yes' and status != 'All':
        prev = set()
        nxt = []
        for sub in submissions:
            if sub['id'] in prev:
                continue
            nxt.append(sub)
            prev.add(sub['id'])
        submissions = nxt[:]
    
    for submission in submissions[:]:
        # basic information about submission
        contestId = submission['contestId']
        submissionId = submission['id']
        problemId = submission['problem']['index']
        fname = str(contestId)+problemId
        
        if len(str(contestId)) > 4:
            print(contestId)
            continue
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
        
# http://192.168.56.1:5000
