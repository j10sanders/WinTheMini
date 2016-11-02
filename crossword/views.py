from flask import render_template
from itertools import groupby
from . import app, rankingint, keygenerator
from .database import session, Entry, followers, User, PWReset
from flask import flash
from flask.ext.login import login_user, logout_user
from getpass import getpass
from werkzeug.security import check_password_hash, generate_password_hash
from .database import User
from flask import request, redirect, url_for
from flask.ext.login import login_required, current_user
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, StaleDataError, UnmappedInstanceError
from ranking import Ranking
from statistics import mean, StatisticsError
import pygal
import json
from urllib.request import urlopen
from pygal.style import BlueStyle
import unittest
import yagmail


@app.route("/")
@app.route("/date/<selected_date>")
def entries(selected_date = ("2017-10-7")):
    #EST = timezone('America/New_York')
    EST = pytz.timezone('US/Eastern')
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc).date()
    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        
    except ValueError:
        selected_date = selected_date[:selected_date.rindex(" ")]
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")

    selected_date = EST.localize(selected_date, is_dst=None).date()

    if selected_date > now_utc:
        selected_date = now_utc

    entries = session.query(Entry)
    
    #determine which entries are oldest and newest, so later can determine if "Older" or "Newer" buttons should be displayed.
    oldestentry = entries.order_by(Entry.datetime.asc()).first()
    newestentry = entries.order_by(Entry.datetime.desc()).first()
    oldesttime = oldestentry.datetime.replace(tzinfo=pytz.utc).astimezone(EST).date()
    newesttime = newestentry.datetime.replace(tzinfo=pytz.utc).astimezone(EST).date()

    older = selected_date - timedelta(1)
    newer = selected_date + timedelta(1)
    
    if selected_date < oldesttime:
        selected_date = oldesttime
    if selected_date > newesttime:
        selected_date = newesttime
        
    
    #datedisplay is used for string version of selecteddate
    datedisplay = datetime.strftime(selected_date, "%b %-d, %Y")
    
    #create a list (entrylist) that has just the entries from a certain day.  This is one of the central pieces of the app.
    entrylist = []
    for entry in entries:
        #convert datetime fron db to EST
        entrytime = entry.datetime
        entrytime = entrytime.replace(tzinfo=pytz.utc).astimezone(EST).date()
        entrytime = entrytime.strftime("%b %-d, %Y")
        
        #define the day before
        daybefore = selected_date - timedelta(1)
        daybefore = daybefore.strftime("%b %-d, %Y")
        
        #what to do when user has selected a day with entriesS
        if entrytime == datedisplay:
            entrylist.append(entry)
            #sort the entries: top score (entry.title) should be at the top
            try: 
                for entry in entrylist:
                    #display the entries in order of best time to worst
                    entry.title = int(entry.title)
                    entrylist.sort(key=lambda x: x.title, reverse = False)
                    
                    #define the next entries that are outside of this day.  These will be converted to "older" and "newer" which is helpful for the buttons "older and "newer" to skip days that have no entries.
                    olderentryid = min(entry.id for entry in entrylist) - 1
                    newerentryid = max(entry.id for entry in entrylist) + 1
            except (ValueError, TypeError):
                flash("There are some non-integers on this page.  Jon needs to fix it so you can see who won :)", "danger")

   
    for entry in entries:
        try:
            if entry.id == olderentryid:
                older = entry.datetime.replace(tzinfo=pytz.utc).astimezone(EST).date()
            if entry.id == newerentryid:
                newer = entry.datetime.replace(tzinfo=pytz.utc).astimezone(EST).date()
        except UnboundLocalError:
            pass
    
    #for statistics, this method is for keeping track of daily scores
    sortedscores = [entry.title for entry in entrylist]
    dayranklist = []
    for day_rank in Ranking(sortedscores, reverse=True):
        dayranklist.append(int(day_rank[0]+1))
    k=0
    
    #collect list of the current_user's followers, so it can be compared in the entries.html with the entry's author_id (to determine if entry is displaoyed to current_user or not)
    current_user_id = current_user.get_id()
    c_follows = session.query(followers).filter_by(follower_id=current_user_id).all()
    c_user_follows = [item[1] for item in c_follows]


    #determine the day_rank of the entries, so the users' stats are tracked:
    for entry in entrylist:
        entry = session.query(Entry).get(entry.id)
        entry.day_rank = day_rank = dayranklist[k]
        session.add(entry)
        k +=1
    session.commit()
    
    streak = 0
    ywinnername = "nobody"
    ywinnerid = "no_id"
    #determine if "newer" and/or "older" links should be shown
    if newestentry in entrylist:
        has_next = True
        has_prev = False
    elif oldestentry not in entrylist:    
        has_next = True
        has_prev = True
    else:
        has_prev = True
        has_next = False
        
    if has_prev == False:
        sevendaysago = selected_date - timedelta(days=8)
        ywinner = session.query(Entry).filter(Entry.datetime >= sevendaysago, Entry.day_rank == (1,)).order_by(Entry.datetime.desc())
        
        #check if there was a tie for first place.  If so, push the winner back to last day
        i = 0
        try:
            while selected_date == ywinner[i].datetime.replace(tzinfo=pytz.utc).astimezone(EST).date():
                #print("i")
                #print(i)
                i += 1
        except IndexError:
            i = i
        
        
        streak = 1
        ywinnerid = ywinner[i+1].user.id
        ywinnername = ywinner[i+1].user.name
        '''for count, x in enumerate(ywinner):
            print(x.user.name, x.datetime, count)'''
        while ywinnername == ywinner[streak+1].user.name:
            streak += 1
        
            #ywinnername = "nobody"
            #ywinnerid = "no_id"
            #streak = 0
        #print(i)

        
        
    return render_template("entries.html",
        entries=entrylist,
        has_next=has_next,
        has_prev=has_prev,
        datedisplay = datedisplay,
        older=older,
        newer=newer,
        current_user_id=current_user_id,
        c_user_follows=c_user_follows,
        streak=streak, 
        ywinnername=ywinnername,
        ywinnerid = ywinnerid
    )
     

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    login_user(user, remember=True)
    flash("Logged in successfully", "success")
    return redirect(request.args.get('next') or url_for("add_entry_get"))
    

@app.route("/register", methods=["GET"])
def register_get():
    return render_template('register.html')

@app.route("/register", methods=["POST"])
def register_post():
    try: 
        if request.form["password"] != request.form["password2"]:
            flash("Your password and password verification didn't match.", "danger")
            return redirect(url_for("register_get"))
        if len(request.form["password"]) < 8:
            flash("Your password needs to be at least 8 characters", "danger")
            return redirect(url_for("register_get"))
        user = User(name=request.form["username"], password=generate_password_hash(request.form["password"]), email=request.form["email"])
        session.add(user)
        allusers = session.query(User).all()
        for users in allusers:
            session.add(user.follow(users))
            session.add(users.follow(user))
        session.commit()
        flash("User successfully registered", "success")
        login_user(user)
        return redirect(request.args.get("next") or url_for("entries"))
    except IntegrityError:
        flash("The username or email was already taken.  This app isn't sophisticated enough to let you reset a password, so just register a new user", "danger")
        session.rollback()
        return redirect(url_for("register_get"))
    
    
@app.route("/entry/<id>", methods=["GET"])
def get_entry(id):
    entry = session.query(Entry)
    return render_template("render_entry.html", entry = entry.get(id))
    
    
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    #print(current_user.name)
    return render_template("add_entry.html")

    
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    try:
        title = int(request.form["title"])
        #title = time
    except ValueError:
        title = request.form["title"]
        if title.count(":") > 1:
            flash(str("You entered something weird.  Your input should be integers (and you might have a semicolon)"), "danger")
            return redirect(url_for("add_entry_get"))
        elif title[0] == ":":
            title = title[1:]
        elif ":" not in title:
            flash(str("You entered something weird.  Your input should be integers (and you might have a semicolon)"), "danger")
            return redirect(url_for("add_entry_get"))
        else:
            title=sum(int(x) * 60 ** i for i,x in enumerate(reversed(title.split(":"))))
    entry = Entry(
        title = title,
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
    
@app.route("/entry/<id>/edit", methods=["GET"])
@login_required
def edit_entry_get(id):
    entry = session.query(Entry)
    return render_template("edit_entry.html", entry = entry.get(id))
    
@app.route("/entry/<id>/edit", methods=["POST"])
def edit_entry_post(id):
    if "cancel" in request.form:
        return redirect(url_for("entries"))
    else:
        entry = session.query(Entry).get(id)
        entry.title = request.form["title"]
        entry.content = request.form["content"].encode('utf-8')
        session.commit()
        return redirect(url_for("entries"))
        
    
@app.route("/entry/<id>/delete", methods=["GET"])
def delete_entry_get(id):
    entry = session.query(Entry)
    return render_template("delete_entry.html", entry = entry.get(id))
        
@app.route("/entry/<id>/delete", methods=["POST"])
def delete_entry_post(id):
    entry = session.query(Entry).get(id)
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/userinfo/<id>", methods=["GET"])
def user_get(id):  
    #Gets specific info for a user based on their ID
    try:
        user = session.query(User).filter_by(id=id).one()
        day_rank = session.query(Entry.day_rank).join(User).filter(Entry.author_id == id).order_by(Entry.datetime.asc()).all()
        ranking = rankingint.toint(day_rank)
        average = mean(ranking)
        average = round(average,1)
        times = session.query(Entry.title).join(User).filter(Entry.author_id == id).order_by(Entry.datetime.asc()).all()
        rankingtimes = rankingint.toint(times)
        avetime = mean(rankingtimes)
        avetime = round(avetime)
        besttime = min(rankingtimes)
        worsttime = max(rankingtimes)
        entryday = session.query(Entry).join(User).filter(Entry.author_id == id).order_by(Entry.datetime.asc()).all()
        entrydaylist = []
        
        for entry in entryday:
        #convert datetime fron db
            entrytime = entry.datetime
            entrytime = entrytime.replace(tzinfo=pytz.utc).date()
            entrytime = entrytime.strftime("%b %-d")
            entrydaylist.append(entrytime)
            

        title = "Seconds to complete"
        graph_of_times = pygal.Line(width=1200, height=600, title=title, style=BlueStyle, fill=True, interpolate='hermite', interpolation_parameters={'type': 'kochanek_bartels', 'b': -1, 'c': 1, 't': 1},
        disable_xml_declaration=True)
        graph_of_times.x_labels = entrydaylist
        graph_of_times.add('Time', rankingtimes)
        
        
        title = "Day Rankings"
        graph_of_rankings = pygal.Bar(width=1200, height=600, title=title, style=BlueStyle, fill=True, interpolate='hermite', interpolation_parameters={'type': 'kochanek_bartels', 'b': -1, 'c': 1, 't': 1},
        disable_xml_declaration=True)
        graph_of_rankings.x_labels = entrydaylist
        graph_of_rankings.add('Day Rank', ranking)
        
        current_user_id = current_user.get_id()
        c_follows = session.query(followers).filter_by(follower_id=current_user_id).all()
        c_user_follows = [item[1] for item in c_follows]
        
        return render_template("userinfo.html", user=user, ranking=ranking, average=average, avetime = avetime, besttime = besttime, worsttime = worsttime, title=title,
                           graph_of_times=graph_of_times, graph_of_rankings = graph_of_rankings, c_user_follows = c_user_follows, current_user_id = current_user_id)
        
    except (NoResultFound, StatisticsError):
        #print("No result found for {0}".format(id))
        flash("Nothing to see there!", "danger")
        return redirect(url_for("stats_get"))
        
    
    
@app.route("/userinfo/<int:id>", methods=["POST"])
@login_required
def follow_post(id):
    user = session.query(User).filter_by(id=id).one()
    cuid = current_user.get_id()
    cuser = session.query(User).filter_by(id=cuid).one()
    try:
        if 'Unfollow' in request.form:
            session.add(cuser.unfollow(user))
            session.commit()
            flash("Good call unfollowing " + user.name +".  Nobody needs that.", "success")
            return redirect(url_for("entries"))
        elif 'Follow' in request.form:
            session.add(cuser.follow(user))
            session.commit()
            flash("You are now following " + user.name +".", "success")
            return redirect(url_for("stats_get"))
    except (IntegrityError, StaleDataError, UnmappedInstanceError):
        flash("That didn't work... mind letting Jon know?", "danger")
        session.rollback()
        return redirect(url_for("entries"))
        
        
@app.route("/stats", methods=["GET"])
def stats_get():
    users = session.query(User).all()
    return render_template("stats.html", users=users)
    
    
    
    
    
@app.route("/pwresetrq", methods=["GET"])
def pwresetrq_get():
    return render_template('pwresetrq.html')
    
@app.route("/pwresetrq", methods=["POST"])
def pwresetrq_post():
    emails = session.query(User.email).all()
    emails = [item[0] for item in emails]
    if request.form["email"] not in emails:
        flash("Your email was never registered.", "danger")
        return redirect(url_for("pwresetrq_get"))
    user = session.query(User).filter_by(email=request.form["email"]).one()
    print(user.id, "is the id")
    key = keygenerator.make_key()
    user_reset = PWReset(reset_key=key, user_id = user.id)
    session.add(user_reset)
    session.commit()
    yag = yagmail.SMTP()
    contents = ['Please go to this URL to reset your password:', "http://workspace2-jonsanders.c9users.io:8080" + url_for("pwreset_get",  id = (str(key))),
                "Email jonsandersss@gmail.com if this doesn't work for you.     'With a Crossword, we're challenging ourselves to make order out of chaos' - Will Shortz"]
    yag.send('jps458@nyu.edu', 'TEST', contents)
    flash(user.name + ", check your email for a link to reset your password.  It expires in a day!", "success")
    return redirect(url_for("entries"))
    
@app.route("/pwreset/<id>", methods=["GET"])
def pwreset_get(id):
    key = id
    return render_template('pwreset.html', id = key)

@app.route("/pwreset/<id>", methods=["POST"])
def pwreset_post(id):
    if request.form["password"] != request.form["password2"]:
        flash("Your password and password verification didn't match.", "danger")
        return redirect(url_for("pwreset_get", id = id))
    if len(request.form["password"]) < 8:
        flash("Your password needs to be at least 8 characters", "danger")
        return redirect(url_for("pwreset_get", id = id))
    user_reset = session.query(PWReset).filter_by(reset_key=id).one()
    #session.query(User).filter_by(id=user_reset.user.id).one()
    #print(user_reset.user_id, "PRINTING ID")
    try:
        session.query(User).filter_by(id = user_reset.user_id).update({'password': generate_password_hash(request.form["password"])})
        session.commit()
    except IntegrityError:
        flash("ERROR", "danger")
        session.rollback()
        return redirect(url_for("entries"))
    
    flash("Your new password is saved.", "success")
    #login_user(user)
    return redirect(url_for("entries"))


'''
#emergency method for getting rid of new entry that is troublesome
@app.route("/deleteit")
def deleteit():
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    newestentry = entries[0]
    
    session.delete(newestentry)
    session.commit()
    return redirect(url_for("entries"))'''
