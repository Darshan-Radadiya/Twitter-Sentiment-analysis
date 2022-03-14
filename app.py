from flask import Flask, render_template, request, session
from textblob import TextBlob
import sys, tweepy
import mysql.connector
from datetime import date

app=Flask(__name__)
app.secret_key="mini"

# conn = mysql.connector.connect(host="remotemysql.com",user="POchGfCDSC",password="quPRIG269Y",database="POchGfCDSC")
conn = mysql.connector.connect(host="localhost",user="root",password="",database="mini")

cursor=conn.cursor()

@app.route("/")
def home():
    return render_template("home.html", label="Register", link="/reg")

@app.route("/reg")
def reg():
    return render_template("regis.html")

@app.route("/add_user", methods=['GET','POST'])
def add_user():
    nm=request.form.get('name')
    em=request.form.get('email')
    us=request.form.get('username')
    ps=request.form.get('pass')

    cursor.execute("""INSERT INTO `users` (`id`,`Name`,`email`,`username`,`password`) VALUES (NULL,'{}','{}','{}','{}')""".format(nm,em,us,ps))
    conn.commit()

    return render_template("login.html", temp="Now you can login")

@app.route("/login")
def log():
    return render_template("login.html")

@app.route("/login_auth", methods=['GET','POST'])
def login_auth():
    us = request.form.get('username')
    ps = request.form.get('pass')
    cursor.execute("""SELECT * FROM `users` WHERE `username` LIKE '{}' AND `password` LIKE '{}'""".format(us,ps))
    selected=cursor.fetchall()
    f = list(selected)
    if len(selected)>0:
        session["user"] = us
        session["id"] = f[0][0]
        return render_template("main.html", user = us, label = "logout", link = "/logout")
    else:
        return render_template("login.html", temp = "Wrong password entered")

@app.route("/main")
def m():
    return render_template("main.html", user = session["user"], label = "logout", link = "/logout")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("home.html", label = "Register", link = "/reg")

@app.route("/pred", methods=["POST","GET"])    
def prediction():
    t = request.form["tweet"]
    n = int(request.form["num"])
    
    consumerKey = 'F1iApk2Z67rz2q57CwevVUw10'
    consumerSecret = 'KdHuH221cESIKv6USqKnaq5EXyW1rTtQNuvMmgwzTKPrAotN4W'
    accessToken = '2472412712-2y2lJNm2kXjzfyeSjt1grDgbXcqaNr7hEvBCbmo'
    accessTokenSecret = 'ct1RCRdhfZL2zOfKbFj91fHRrTP3BI47v6n9kqEApC201'

    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    tweets = tweepy.Cursor(api.search, q=t, lang="en").items(n)

    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    for page in tweets:
    # print("tweet is",ok.text)
        analysis=TextBlob(page.text)
        polarity += analysis.sentiment.polarity
        
        if(analysis.sentiment.polarity == 0):
            neutral += 1
        if(analysis.sentiment.polarity < 0):
            negative += 1
        if(analysis.sentiment.polarity > 0):
            positive += 1


    positive = 100*(float(positive)/float(n))
    negative = 100*(float(negative)/float(n))
    neutral = 100*(float(neutral)/float(n))

    pos = format(positive, '.2f')
    neg = format(negative, '.2f')
    neu = format(neutral, '.2f')
    # pos = int(positive)
    # neg = int(negative)
    # neu = int(neutral)

    cursor.execute("""INSERT INTO `history` (`id`,`username`,`date`,`tweet`,`total_tweets`,`positive`,`negative`,`neutral`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')""".format(session["id"],session["user"],date.today(),t,n,pos,neg,neu))    
    conn.commit()

    return render_template("result.html", p=pos, n=neg, nt=neu)


    
if __name__ == '__main__':
    app.run(debug=True)