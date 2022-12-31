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
import shutil
app = Flask(__name__)

executor = Executor(app)

@app.route("/start", methods = ['get'])
def post():
    handle = request.args.get('handle')
    status = request.args.get('status')
    # OK = AC
    # RUNTIME_ERROR = RTE
    # WRONG_ANSWER = WA
    # TIME_LIMIT_EXCEEDED = TLE
    unique = request.args.get('unique')
    # "Yes" = unique
    rid = hash(handle+status+unique+str(random.randint(1,int(1e9)+7)))
    executor.submit(get_submissions,handle,status,unique,rid)
    return rid

@app.errorhandler(404)
def page_not_found(error):
    return "<h1> 404: Page not found <h1>"

def get_submissions(handle, status, unique, rid):
    
    # in case people troll
    if not handle or not status or not unique:
        '''
        do sql shit here
        Send it in the form of database[rid] = {"status": "failed", "payload": 0}
        '''
        return

    '''
    do sql shit here
    send it in the form of database[rid] = {"status": "starting", "payload": 0}
    '''

    # uniqueness
    unique = unique=='Yes'

    # path to submission folder
    path = "submissions\\"

    # submission limit
    limit = 10000
    
    # get submission ids
    handleurl = "https://codeforces.com/api/user.status?handle={}&from=1&count={}".format(handle, limit)
    response = requests.get(handleurl)
    submissions = json.loads(response.text)['result']

    # check for existing files
    if os.path.isdir(path):
        shutil.rmtree('submissions')
    os.mkdir('submissions')

    # pause to not get rate limited by the cf server 
    time.sleep(1)

    # filter status
    if status != 'All':
        submissions = list(filter(lambda submission: submission['verdict'] == status, submissions))

    # maintain set of source codes for uniquness
    exist = dict()

    # counting
    prev = set()
    nxt = []
    for sub in submissions:
        name = str(sub['contestId'])+sub['problem']['index']
        if name in prev:
            continue
        nxt.append(sub)
        prev.add(name)
        exist[name] = 0
    if unique: submissions = nxt[:]

    print(exist)
    for submission in submissions[:]:
        print("__________________________________________________________")
        # basic information about submission
        contestId = submission['contestId']
        submissionId = submission['id']
        problemId = submission['problem']['index']
        fname = str(contestId)+problemId
        print(fname,submissionId)
        
        # gym or something, its private so we can't scrape the code :(
        if len(str(contestId)) > 4:
            print(contestId)
            continue

        # if we want unique then skip duplicates
        if unique and exist[fname]: continue


        print("Processing... {}".format(fname))
        suburl = "https://codeforces.com/contest/{}/submission/{}".format(contestId,submissionId)
        print(suburl)
        cnt = 0
        # basically if codeforces is stupid and makes you try again, then you wait 30 seconds before trying agian
        # if it doesnt work after waiting for 30 seconds, just skip it idk what to do i hate codeforces 
        while True:
            try:
                cnt += 1
                response = requests.get(suburl)
                sub = response.text
                content = bs4.BeautifulSoup(sub, "html.parser")
                codecont = content.find_all("pre", {"id": "program-source-text"})[0]
                # break here because error would be thrown if codeforces is dumb and wont give me the actual submission but instead redirects me to the main  page
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

        # get more info about the code
        lang = codecont['class'][1][5:]
        code = codecont.getText()
        
        # remove extra whitespace (could be a problem if you have "\r\n" in your code but who does that)
        code = code.replace("\r\n", "\n")
        
        # real file name (wow)
        realfilename = path+fname

        # not unique case, we just add a number to each sub
        if not unique: realfilename += '-'+str(exist[fname])
        realfilename += "."+lang

        # write to file
        f = open(realfilename,"w")
        f.write(str(code))
        f.close()

        # increment for not unique case and keeping track of already visited
        exist[fname] += 1
        
        '''
        Daniel do your SQL shit here

        basically send to "rid" how many files you've gone through, like 69 out of 420
        so i can use it to make progress bar

        Send it in the form of database[rid] = {"status": "downloading", "payload": (69,420)}
        '''
        
        # pause or else codeforces big stupid
        time.sleep(5)

    
# replace 192.168.56.1 with your actual IPv4 address
# flask run -h 192.168.56.1
# http://192.168.56.1:5000
