from flask import render_template
from itertools import groupby
from . import app
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


@app.route("/")
@app.route("/date/<selected_date>")
def entries(selected_date = str(datetime.now())):
    EST = timezone('America/New_York')
    now = datetime.now(EST)
    
    print(selected_date)
    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        selected_date = selected_date.replace(tzinfo=pytz.utc).astimezone(EST).date()
        
        #selected_date = selected_date.replace(tzinfo=pytz.utc).astimezone(EST)
    except ValueError:
        selected_date = selected_date[:selected_date.rindex(" ")]
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        selected_date = selected_date.replace(tzinfo=pytz.utc).astimezone(EST).date()
    print(selected_date)

    # Zero-indexed page
    #page_index = page - 1
    i = 0
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())

    oldestentry = entries[-1]
    newestentry = entries[0]
    entrylist = []
    count = session.query(Entry).count()
    
    older = selected_date - timedelta(1)
    newer = selected_date + timedelta(1)
    print(newer)
    #create a list (entrylist) that has just the entries from a certain day.
    for entry in entries:
        entrytime = entry.datetime
        entrytime = entrytime.replace(tzinfo=pytz.utc).astimezone(EST)
        print(entrytime)
        entrytime = entrytime.strftime("%Y-%m-%d")

        daybefore = selected_date - timedelta(i)
        daybefore = daybefore.strftime("%Y-%m-%d")
        print(daybefore, "daybefore")
        if entrytime == daybefore:
            entrylist.append(entry)
            print(entrylist)
    if entrylist == []:
        selected_date = selected_date - timedelta(1)
        return redirect(url_for("entries", selected_date = selected_date))
                
            
    #NEED A NEW/SEPERATE METHOD FOR NEWER.**************
    
    #Trying to classify a winner here
    
        
    limit= len(entrylist)
    total_pages = (count - 1) / limit + 1
    
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
        selected_date=selected_date,
        older=older,
        newer=newer,
        total_pages=total_pages
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
    login_user(user, remember=True, force=True)
    flash('Logged in successfully')
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
    return render_template("render_entry.html", entry = entry.get(id))
    
    
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

    
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    time = request.form["title"]
    if time[0] == ":":
        title = time
    elif ":" not in time:
        title = time
    else:
        title=sum(int(x) * 60 ** i for i,x in enumerate(reversed(time.split(":"))))
    #print(sum(int(x) * 60 ** i for i,x in enumerate(reversed(time.split(":")))))
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
        entry.content = request.form["content"]
        entry.datetime = request.form
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
    
    
