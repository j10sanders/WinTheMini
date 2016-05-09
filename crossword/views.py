from flask import render_template
from itertools import groupby
from . import app
from .database import session, Entry
from flask import flash
from flask.ext.login import login_user, logout_user
from werkzeug.security import check_password_hash
from .database import User
from flask import request, redirect, url_for
from flask.ext.login import login_required, current_user
import datetime
from datetime import date, timedelta

@app.route("/")
@app.route("/date/<selected_date>")
def entries(selected_date = str(datetime.date.today())):
    selected_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
    print(selected_date)
    # Zero-indexed page
    #page_index = page - 1
    older = selected_date - timedelta(1)
    print(older)
    older = older.strftime("%Y-%m-%d")
    newer = selected_date + timedelta(1)
    newer = newer.strftime("%Y-%m-%d")
    print(newer)
    entrylist = []
    count = session.query(Entry).count()
    i = 0
    while entrylist == []:
        entries = session.query(Entry)
        entries = entries.order_by(Entry.datetime.desc())
        oldestentry = entries[-1]
        newestentry = entries[0]
        for entry in entries:
            daybefore = selected_date - timedelta(i)
            if entry.datetime.strftime("%Y-%m-%d") == daybefore.strftime("%Y-%m-%d"):
                entrylist.append(entry)
                print(entrylist)
        if entrylist == []:
            i += 1
            print(entrylist)
            print(daybefore)
    #selected_date = daybefore
        
    limit= len(entrylist)
    total_pages = (count - 1) / limit + 1
    
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
        older = older,
        newer = newer,
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
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
    
@app.route("/entry/<id>/edit", methods=["GET"])
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
    
