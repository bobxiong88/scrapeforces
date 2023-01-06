from flask import Flask, render_template, redirect, request, send_file
from flask_executor import Executor
import json
from time import sleep
import bs4
import time
import os
import requests
import random
import shutil
import mysql.connector as mysql
import traceback
import flask

HOST = "sql9.freemysqlhosting.net" # or "domain.com"
DATABASE = "sql9587489"
USER = "sql9587489"
PASSWORD = "cxs48SNIsG"
mydb = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
'''
mydb = mysql.connect(
    host = "sql.freedb.tech",
    user = "freedb_okayman",
    password = "Z*&5a@@DMwwSnH5",
    database = "freedb_scrapeforces")
'''
print("Connected to:", mydb.get_server_info())

mycursor = mydb.cursor(buffered = True)

app = Flask(__name__)
app.debug = True

executor = Executor(app)

end = False

@app.route("/start", methods = ['get'])
def post():
    try:
        handle = request.args.get('handle')
        status = request.args.get('status')
        unique = request.args.get('unique')
        
        rid = hash(handle+status+unique+str(random.randint(1,int(1e9)+7)))%(int(1e9)+7)+random.randint(1,int(1e10))

        mycursor.execute("INSERT INTO progress (rid, status, current, total) VALUES (%s, %s, %s, %s)", (rid, "starting", 0, 0))
        mydb.commit()
        time.sleep(1)
        
        executor.submit(get_submissions,handle,status,unique,rid)
        
        res = flask.jsonify({"rid": rid})
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res
    except Exception:
        traceback.print_exc()


@app.route("/get_status", methods = ['get'])
def get_status():
    mid = request.args.get('rid')
    print("okay status id is ", mid)
    cur = (mid, 'failed', 100,100)
    try:
        print("BEFORE")
        mycursor.execute("SELECT * FROM progress")
        print("DURING")
        for x in mycursor:
            print(tuple(x))
            if str(x[0]) == str(mid):
                cur = tuple(x)
                break
        print("AFTER")
    except Exception:
        print("there is error in get_status")
        traceback.print_exc()
    print("cur is ", cur)
    res = {"rid":cur[0],
           "status":cur[1],
           "current":cur[2],
           "total":cur[3]}
    res = flask.jsonify(res)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

@app.route("/download", methods = ['get'])
def download():
    rid = request.args.get('rid')
    fname = str(rid)+'.zip'
    res = send_file(fname,fname)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

@app.route("/done", methods = ['get'])
def done():
    rid = request.args.get('rid')
    mycursor.execute("DELETE FROM progress WHERE rid = %s", (rid,))
    mydb.commit()
    if os.path.isdir(str(rid)):
        shutil.rmtree(str(rid))
    if os.path.exists(str(rid)+'.zip'):
        os.remove(str(rid)+'.zip')
    res = {"hi":0}
    res = flask.jsonify(res)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

@app.errorhandler(404)
def page_not_found(error):
    return "<h1> 404: Page not found <h1>"

def get_submissions(handle, status, unique, rid):
    try:
        end = False
        # in case people troll
        
        '''
        do sql shit here
        send it in the form of database[rid] = {"status": "starting", "payload": 0}
        '''

        # uniqueness
        print(handle,status,unique)
        unique = unique=='Yes'
        print("processing:", handle, status, unique)

        # path to submission folder
        path = "{}\\".format(rid)

        # submission limit
        limit = 10
        
        # get submission ids
        handleurl = "https://codeforces.com/api/user.status?handle={}&from=1&count={}".format(handle, limit)
        response = requests.get(handleurl)
        stat = json.loads(response.text)['status']
        
        if stat == 'FAILED':
            print("here")
            mycursor.execute("UPDATE progress SET status = %s WHERE rid = %s", ("failed", rid))
            mydb.commit()
            return
        
        submissions = json.loads(response.text)['result']

        # check for existing files
        if os.path.isdir(path):
            print("exist")
            shutil.rmtree(str(rid))
        os.mkdir(str(rid))
        print("made", str(rid))
        print("submissions created",rid)

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
            if end: break
            name = str(sub['contestId'])+sub['problem']['index']
            if name in prev:
                continue
            nxt.append(sub)
            prev.add(name)
            exist[name] = 0
        if unique: submissions = nxt[:]
        
        mycursor.execute("UPDATE progress SET status = %s, current = %s, total = %s WHERE rid = %s", ("downloading", 0, len(submissions), rid))
        mydb.commit()

        print("# of subs: ", len(submissions))
        
        print(exist)
        
        sub_count = 0;
        for submission in submissions[:]:
            # Update
            sub_count += 1
            
            time.sleep(1)
            mycursor.execute("UPDATE progress SET status = %s, current = %s WHERE rid = %s", ("downloading", sub_count, rid))
            mydb.commit()
            time.sleep(1)

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
            print("whileballs")
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
            with open(realfilename, "w", encoding="utf-8") as f:
                f.write(code)

            # increment for not unique case and keeping track of already visited
            exist[fname] += 1

            # pause or else codeforces big stupid
            time.sleep(1)
        
        shutil.make_archive(str(rid), 'zip', path)
        
        # Finished
        mycursor.execute("UPDATE progress SET status = %s, current = %s WHERE rid = %s", ("finished", len(submissions), rid))
        mydb.commit()

        # check if it worked
        mycursor.execute("SELECT * FROM progress")
        for x in mycursor:
            print(x)
            
    except Exception:
        traceback.print_exc()
    
# replace 192.168.56.1 with your actual IPv4 address
# flask run -h 192.168.56.1
# http://192.168.56.1:5000
# http://192.168.56.1:5000/start?handle=bobxiong88&status=OK&unique=Yes
