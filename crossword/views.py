from flask import render_template
from itertools import groupby
from . import app, rankingint
from .database import session, Entry
from flask import flash
from flask.ext.login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from .database import User
from flask import request, redirect, url_for
from flask.ext.login import login_required, current_user
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from ranking import Ranking
from statistics import mean
#from scipy.stats import rankdata


@app.route("/")
@app.route("/date/<selected_date>")
def entries(selected_date = ("2017-6-7")):
    EST = timezone('America/New_York')
    now = datetime.now(EST)
    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        
    except ValueError:
        selected_date = selected_date[:selected_date.rindex(" ")]
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    if selected_date > now.date():
        selected_date = now.date()
    # Zero-indexed page
    #page_index = page - 1
    i = 1
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    #print(session.query(Entry.author_id).order_by(Entry.title).all(), "author_id's")
    
    oldestentry = entries[-1]
    newestentry = entries[0]
    oldesttime = oldestentry.datetime.date()
    entrylist = []
    
    #datedisplay is used for string version of selecteddate
    datedisplay = datetime.strftime(selected_date, "%b %-d, %Y")
    older = selected_date - timedelta(1)
    newer = selected_date + timedelta(i)

    #create a list (entrylist) that has just the entries from a certain day.
    for entry in entries:
        entrytime = entry.datetime
        entrytime = entrytime.replace(tzinfo=pytz.utc).astimezone(EST).date()
        entrytime = entrytime.strftime("%b %-d, %Y")
        
        daybefore = selected_date - timedelta(1)
        daybefore = daybefore.strftime("%b %-d, %Y")
        if entrytime == datedisplay:
            entrylist.append(entry)
            #sort the entries: top score (entry.title) should be at the top
            try: 
                for x in entrylist:
                    entry.title = int(entry.title)
                    #print(entry.title)
                    entrylist.sort(key=lambda x: x.title, reverse = False)
                    olderentryday = min(entry.id for entry in entrylist) - 1
                    newerentryday = max(entry.id for entry in entrylist) + 1
            except (ValueError, TypeError):
                flash("There are some non-integers on this page.  Jon needs to fix it so you can see who won :)", "danger")
        
        
    
    for entry in entries:
        try:
            if entry.id == olderentryday:
                olderentryday = entry.datetime.date()
                #print(preventryday)
                older = olderentryday
                
        except UnboundLocalError:
            pass
            
    
    if entrylist == []:
        if selected_date < oldesttime:
            return redirect(url_for("entries", selected_date = oldesttime))
        else:
            selected_date = older
            return redirect(url_for("entries", selected_date = selected_date))
                
    sortedscores = [ entry.title for entry in entrylist]
    #print(sortedscores, "sorted scores")
    dayranklist = []
#try:
    for day_rank in Ranking(sortedscores, reverse=True):
        dayranklist.append(int(day_rank[0]+1))
        #print(dayranklist)
        #list(map(int, dayranklist))
    k=0
    for entry in entrylist:
        entry = session.query(Entry).get(entry.id)
        #entry = session.query(Entry).get(entry_id)
        #print(entry, "id?")
        entry.day_rank = day_rank = dayranklist[k]
        #print(entry, entry.day_rank)
        #print(entry.id, "entry.id")
        session.add(entry)
        #print(entry.day_rank)
        k +=1
    session.commit()
    #except (ValueError, TypeError):
        #pass
    #print(dayranklist, "dayranklist")
    

    #NEED A NEW/SEPERATE METHOD FOR NEWER.**************
    #determine "newer" and/or "older" links should be shown
    if newestentry in entrylist:
        has_next = True
        has_prev = False
    elif oldestentry not in entrylist:    
        has_next = True
        has_prev = True
    else:
        has_prev = True
        has_next = False

    return render_template("entries.html",
        entries=entrylist,
        has_next=has_next,
        has_prev=has_prev,
        datedisplay = datedisplay,
        older=older,
        newer=newer,
    )
     
     
@app.route("/deleteit")
def deleteit():
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    newestentry = entries[0]
    
    session.delete(newestentry)
    session.commit()
    return redirect(url_for("entries"))

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
    flash('Logged in successfully')
    #print(current_user)
    return redirect(request.args.get('next') or url_for("add_entry_get"))
    

@app.route("/register", methods=["GET"])
def register_get():
    return render_template('register.html')

@app.route("/register", methods=["POST"])
def register_post():
    try: 
        name = User(name=request.form["username"], password=generate_password_hash(request.form["password"]), email=request.form["email"])
        session.add(name)
        session.commit()
        flash("User successfully registered")
        login_user(name)
        return redirect(request.args.get("next") or url_for("entries"))
    except IntegrityError:
        flash("The username or email was already taken.  This app isn't sophisticated enough to let you reset a password, so just register a new user", "danger")
        return redirect(url_for("register_get"))
    
    
@app.route("/entry/<id>", methods=["GET"])
def get_entry(id):
    entry = session.query(Entry)
    #print(current_user)
    return render_template("render_entry.html", entry = entry.get(id))
    
    
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    #print(current_user)
    return render_template("add_entry.html")

    
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    #print(current_user)
    try:
        time = int(request.form["title"])
        title = time
    except ValueError:
        time = request.form["title"]
        if time.count(":") > 1:
            flash(str("You entered something weird.  Your input should be integers (and you might have a semicolon)"), "danger")
            return redirect(url_for("add_entry_get"))
        elif time[0] == ":":
            title = time[1:]
        elif ":" not in time:
            flash(str("You entered something weird.  Your input should be integers (and you might have a semicolon)"), "danger")
            return redirect(url_for("add_entry_get"))
        else:
            title=sum(int(x) * 60 ** i for i,x in enumerate(reversed(time.split(":"))))
    entry = Entry(
        title = title,
        content=request.form["content"],
        #content=request.form["content"].encode('utf-8'),
        author=current_user
    )
    #print(entry.content)
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
        #entry.content = request.form["content"]
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

@app.route("/stats", methods=["GET"])
def stats_get():
    users = session.query(User).all()
    #entries = session.query(Entry).all()
    day_rank = session.query(Entry.day_rank).all()
    entries = session.query(Entry.day_rank).join(User).order_by(Entry.datetime.desc())
    ranking = rankingint.toint(entries)
    average = mean(ranking)

    return render_template("stats.html", users=users, entries=entries, average=average, day_rank=day_rank)


@app.route("/userinfo/<id>")
def user_get(id):  
    """Gets specific info for a user based on their ID"""
    try:
        user = session.query(User).filter_by(id=id).one()
        day_rank = session.query(Entry.day_rank).join(User).filter(Entry.author_id == id).all()
        ranking = rankingint.toint(day_rank)
        average = mean(ranking)
        average = round(average,1)
        #print(ranking, "iufrhfniurshn")
        #print(day_rank)
        #average = mean(ranking)
        #print(average)
        #entries = session.query(Entry).join(User).filter(Entry.author_id = id).one()
    except NoResultFound:
        #print("No result found for {0}".format(id))
        user = None
    return render_template("userinfo.html", user=user, ranking=ranking, average=average)