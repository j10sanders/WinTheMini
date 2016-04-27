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

    
#PAGINATE_BY = len(session.query(Entry).count())
PAGINATE_BY = 10


@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    try:
        limit = int(request.args.get("limit", PAGINATE_BY))
        #try and if get value error, set limit to paginate_by
        
        # Zero-indexed page
        page_index = page - 1
    
        count = session.query(Entry).count()
    
        start = page_index * limit
        end = start + limit
    
        total_pages = (count - 1) / limit + 1
        has_next = page_index < total_pages - 1
        has_prev = page_index > 0
        
        end_date = (datetime.datetime.now)
        start_date = end_date - datetime.timedelta(days=4)
        
        
        entries = session.query(Entry)
        entries = entries.order_by(Entry.datetime.desc())
        
        for entry in entries:
            if entry.datetime > start_date:
                print(entry)
        
        entries = entries[start:end]
        
        return render_template("entries.html",
            entries=entries,
            has_next=has_next,
            has_prev=has_prev,
            page=page,
            total_pages=total_pages
        )
    except ValueError:
        flash(u'Try a whole number between 1 - 50!', 'danger')
        limit = PAGINATE_BY
        page_index = page - 1
    
        count = session.query(Entry).count()
    
        start = page_index * limit
        end = start + limit
    
        total_pages = (count - 1) / limit + 1
        has_next = page_index < total_pages - 1
        has_prev = page_index > 0
    
        entries = session.query(Entry)
        entries = entries.order_by(Entry.datetime.desc())
        entries = entries[start:end]
        
        return render_template("entries.html",
            entries=entries,
            has_next=has_next,
            has_prev=has_prev,
            page=page,
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
    
