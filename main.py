
from types import TracebackType
from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from __init__ import create_app, db

import re
import json
from urllib.request import urlopen

import collections
from typing import Counter
#from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for
import datetime
from pymongo import results
from base62 import idToShortURL
import pymongo
from pymongo import MongoClient
from pymongo import collection
import datetime
cluster=MongoClient('mongodb+srv://srasti:1234@cluster0.mxdta.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db1=cluster['url_shortner']
collection=db1['urlmap']


main = Blueprint('main', __name__)

@main.route('/') # home page that return 'index'
def index():
    return render_template('index.html')

@main.route('/profile', methods=('GET', 'POST')) # profile page that return 'profile'
@login_required
def profile():
    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('main.index'))
        f=open('counter.txt')
        Counter=int(f.read())
        f.close()
        f=open('counter.txt','w')
        f.write(str(Counter+1))
        f.close()
        print(Counter)
        short_url_code=idToShortURL(Counter)
        date=datetime.datetime.now()
        formated_date=str(date.date())+" "+str(date.hour)+":"+str(date.minute)+":"+str(date.second)
        post={"_id":short_url_code,"original_url":url,"clicks":0,"timestamp":formated_date,"email":current_user.email,"traffic_time":[],"locations":[]}
        collection.insert_one(post)

        short_url = request.host_url + short_url_code

        return render_template('profile.html', name=current_user.name, short_url=short_url)

    return render_template('profile.html', name=current_user.name)
    #return render_template('profile.html', name=current_user.name)

@main.route('/<id>')
def url_redirect(id):

    if id:
        try:
            url = 'http://ipinfo.io/json'
            response = urlopen(url)
            data = json.load(response)
            IP=data['ip']
            org=data['org']
            city = data['city']
            country=data['country']
            region=data['region']

            result=collection.find_one({"_id":id})

            clicks=result['clicks']
            collection.update_one({"_id" : id},{ "$set": { "clicks" : clicks+1}})

            date=datetime.datetime.now()
            formated_date=str(date.date())+" "+str(date.hour)+":"+str(date.minute)+":"+str(date.second)
            collection.update_one({"_id" : id},{"$push": {"traffic_time":formated_date}})

            collection.update_one({"_id" : id},{"$push": {"locations":country}})


            try:
                return redirect(result['original_url'])
            except Exception as e:
                flash('Invalid URL')
                return redirect(url_for('main.profile'))
        except:
            flash('Invalid URL')
            return redirect(url_for('main.profile'))
    else:
        flash('Invalid URL')
        return redirect(url_for('main.profile'))

@main.route('/stats2')
def stats():
    results=collection.find({"email":current_user.email})
    urls = []
    for url in results:
        url = dict(url)
        url['short_url'] = request.host_url + url['_id']
        urls.append(url)

    return render_template('stats2.html', urls=urls)

app = create_app() # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    db.create_all(app=create_app()) # create the SQLite database
    app.run(debug=True) # run the flask app on debug mode