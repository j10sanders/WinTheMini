from flask import render_template, render_template_string, flash, request
from flask import redirect, url_for
from itertools import groupby
from . import app, rankingint, keygenerator, quotes
from .database import session, Entry, followers, User, PWReset
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.login import current_user
from getpass import getpass
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import Forbidden
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, StaleDataError
from sqlalchemy.orm.exc import UnmappedInstanceError
from ranking import Ranking
from statistics import mean, StatisticsError
import pygal
import json
from pygal.style import BlueStyle
import unittest
import yagmail
from sparkpost import SparkPost
import os



@app.route("/")
@app.route("/date/<selected_date>")
def entries(selected_date=("2017-12-7")):
    no_redirect=request.args.get('no_redirect')
    no_redirect = (no_redirect == "True")
    # EST = timezone('America/New_York')
    EST = pytz.timezone('US/Eastern')
    now_est = datetime.now(EST).date()
    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
    except ValueError:
        selected_date = selected_date[:selected_date.rindex(" ")]
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
    selected_date = EST.localize(selected_date, is_dst=None).date()
    
    
    # instead of entries = session.query(Entry), make a smaller query
    daysago = (datetime.now() - timedelta(days=100)).date()
    selectedago = (selected_date - timedelta(days=30))
    if selectedago < daysago:
        daysago = selectedago
    entries = session.query(Entry).filter(Entry.datetime >= daysago)
    
    # Determine which entries are oldest and newest,
    # so later can determine if "Older" or "Newer" buttons should be displayed.
    oldest = entries.order_by(Entry.datetime.asc()).first()
    newest = entries.order_by(Entry.datetime.desc()).first()
    oldesttime = oldest.datetime.replace(tzinfo=pytz.utc).astimezone(EST)
    oldesttime = oldesttime.date()
    newesttime = newest.datetime.replace(tzinfo=pytz.utc).astimezone(EST)
    newesttime = newesttime.date()

    older = selected_date - timedelta(1)
    newer = selected_date + timedelta(1)

    if selected_date < oldesttime:
        selected_date = oldesttime
    if selected_date > newesttime:
        selected_date = newesttime
        
    # Datedisplay is used for string version of selected_date
    datedisplay = datetime.strftime(selected_date, "%b %-d, %Y")

    # Create a list (entrylist) that has just the entries from a certain day.
    # This is one of the central pieces of the app.
    entrylist = []
    for entry in entries:
        # Convert datetime fron db to EST
        entrytime = entry.datetime
        entrytime = entrytime.replace(tzinfo=pytz.utc).astimezone(EST).date()
        entrytime = entrytime.strftime("%b %-d, %Y")

        # Define the day before
        daybefore = selected_date - timedelta(1)
        daybefore = daybefore.strftime("%b %-d, %Y")

        # What to do when user has selected a day with entriesS
        if entrytime == datedisplay:
            entrylist.append(entry)
            # Sort the entries: top score (entry.title) should be at the top
            try: 
                for entry in entrylist:
                    #display the entries in order of best time to worst
                    entry.title = int(entry.title)
                    entrylist.sort(key=lambda x: x.title, reverse = False)
                    
                    # Define the next entries that are outside of this day.
                    # They will be converted to "older" and "newer" which is
                    # helpful for the buttons "older and "newer" to skip days
                    # that have no entries
                    olderentryid = min(entry.id for entry in entrylist) - 1
                    oldernotdeleted = (entries.filter(Entry.id <= olderentryid)
                    .order_by(Entry.datetime.desc()).first())
                    newerentryid = max(entry.id for entry in entrylist) + 1
                    newernotdeleted = (entries.filter(Entry.id >= newerentryid)
                    .order_by(Entry.datetime.asc()).first())
            except (ValueError, TypeError):
                flash("There are some non-integers on this page." +
                " Jon needs to fix it so you can see who won :)", "danger")

    
    for entry in entries:
        try:
            if entry.id == oldernotdeleted.id:
                older = (entry.datetime.replace(tzinfo=pytz.utc)
                .astimezone(EST).date())
            if entry.id == newernotdeleted.id:
                newer = (entry.datetime.replace(tzinfo=pytz.utc)
                .astimezone(EST).date())
        except (UnboundLocalError, AttributeError):
            pass
        
    entry_authors = []
    # For statistics, this method is for keeping track of daily scores.
    # Don't do this every time the page is visited, just if the day is today

    if now_est - selected_date <= timedelta(days=0):
        sortedscores = [entry.title for entry in entrylist]
        dayranklist = []
        for day_rank in Ranking(sortedscores, reverse=True):
            dayranklist.append(int(day_rank[0]+1))
        k = 0
        
        # Determine the day_rank of the entries, so the users' stats are tracked:
        for entry in entrylist:
            entry = session.query(Entry).get(entry.id)
            entry.day_rank = day_rank = dayranklist[k]
            entry_authors.append(entry.author_id)
            session.add(entry)
            k += 1
        session.commit()
    
    # Collect list of the current_user's followers, so it can be compared in
    # the entries.html with the entry's author_id (to determine if
    # entry is displayed to current_user or not)
    current_user_id = current_user.get_id()
    # Don't want to compare Nonetype to ints later
    if current_user_id is not None:
        current_user_id = int(current_user_id)
    else:
        current_user_id = 0
    c_follows = (session.query(followers)
    .filter_by(follower_id=current_user_id).all())
    c_user_follows = [item[1] for item in c_follows]

    streak = 0
    ywinnername = "nobody"
    ywinnerid = "no_id"

    # Can anyone view?
    today = False
    dateshowing = "today"
    
    tiers = []
    dt = datetime.now()
    if (dt.now(EST).isoweekday() >=6 and dt.now(EST).hour >=10) or dt.now(EST).hour >=19:
        newday = True
    else:
        newday = False
    # Determine if "newer" and/or "older" links should be shown
    if newest in entrylist:
        has_next = True
        has_prev = False
    elif oldest not in entrylist:
        has_next = True
        has_prev = True
    else:
        has_prev = True
        has_next = False
    if has_prev is False:
        today = True
        sevendaysago = selected_date - timedelta(days=8)
        ywinner = entries.filter(Entry.datetime >= sevendaysago,
                                 Entry.day_rank ==
                                 (1,)).order_by(Entry.datetime.desc())
        if now_est > selected_date or newday is True:
            dateshowing = "old"

        # Check if there is a tie for first place today.  If so, push the winner
        # back to last day
        i = 0
        try:
            while selected_date == (ywinner[i].datetime
            .replace(tzinfo=pytz.utc).astimezone(EST).date()
            ):
                i += 1
        except IndexError:
            i = i
        # Determine streak count for who won the last consecutive days
        if ywinner.count() > i:
            if dateshowing == "old":
                ywinnerid = ywinner[0].user.id
                ywinnername = ywinner[0].user.name
            else:
                ywinnerid = ywinner[i].user.id
                ywinnername = ywinner[i].user.name
        try:
            while ywinnername == ywinner[streak+i].user.name:
                streak += 1
        except IndexError:
            streak = streak
        
        if dateshowing != "old":
            y = selected_date - timedelta(days=1)
        else:
            y = selected_date
        for x in ywinner:
            if x.datetime.replace(tzinfo=pytz.utc).astimezone(EST).date() == y:
                tiers.append(x.user.name)
        tiers = len(tiers)
    quote = quotes.quote_me()
    if tiers == []:
        tiers = 0
    
    if no_redirect is True:
        return render_template("entries.html",
                       entries=entrylist,
                       has_next=has_next,
                       has_prev=has_prev,
                       datedisplay=datedisplay,
                       older=older,
                       newer=newer,
                       current_user_id=current_user_id,
                       c_user_follows=c_user_follows,
                       streak=streak,
                       ywinnername=ywinnername,
                       ywinnerid=ywinnerid,
                       dateshowing=dateshowing,
                       entry_authors=entry_authors,
                       today=today,
                       quotes=quote,
                       tiers=tiers,
                       no_redirect=no_redirect,
                       )
        
    if current_user_id != 0:
        if (current_user_id not in entry_authors and today is True):
            if dateshowing == "old":
                older = selected_date - timedelta(days=1)
            return redirect(url_for("add_entry_get", add_entry_older = str(older), 
                            streak=streak,
                            tiers=tiers, ywinnername=ywinnername))

    return render_template("entries.html",
                           entries=entrylist,
                           has_next=has_next,
                           has_prev=has_prev,
                           datedisplay=datedisplay,
                           older=older,
                           newer=newer,
                           current_user_id=current_user_id,
                           c_user_follows=c_user_follows,
                           streak=streak,
                           ywinnername=ywinnername,
                           ywinnerid=ywinnerid,
                           dateshowing=dateshowing,
                           entry_authors=entry_authors,
                           today=today,
                           quotes=quote,
                           tiers=tiers,
                           )


@app.route("/login", methods=["GET"])
def login_get():
    current_user_id = current_user.get_id()
    # Don't want to compare Nonetype to ints later
    if current_user_id is not None:
        current_user_id = int(current_user_id)
        user_object = session.query(User).filter_by(id=current_user_id).one()
        
        flash(user_object.name + ", you are logged in.  Feel free to login if" +
        " you are someone else though.", "warning")
    else:
        current_user is None
    
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
            flash("Your password and password verification didn't match.",
                  "danger")
            return redirect(url_for("register_get"))
        if len(request.form["password"]) < 8:
            flash("Your password needs to be at least 8 characters", "danger")
            return redirect(url_for("register_get"))
        user = User(name=request.form["username"],
                    password=generate_password_hash(request.form["password"]),
                    email=request.form["email"])
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
        flash("The username or email was already taken." +
              " Maybe you need to reset your password (below)?", "danger")
        session.rollback()
        return redirect(url_for("register_get"))


@app.route("/entry/<id>", methods=["GET"])
def get_entry(id):
    entry = session.query(Entry)
    return render_template("render_entry.html", entry=entry.get(id))


@app.route("/entry/add/", methods=["GET", "POST"])
@login_required
def add_entry_get(add_entry_older=None):
    if request.method=='GET':
        older=request.args.get('add_entry_older')
        #ywinnerid=request.args.get('ywinnerid') 
        #c_user_follows=request.args.get('c_user_follows')
        streak=request.args.get('streak')
        #current_user_id=request.args.get('current_user_id')
        tiers=request.args.get('tiers')
        ywinnername=request.args.get('ywinnername')
        if older:
            #older=datetime.strptime(older, "%Y-%m-%d")
            return render_template("add_entry.html", older=older,
            #ywinnerid=ywinnerid,
            streak=int(streak),
            tiers=int(tiers), ywinnername=ywinnername)
        else:
            return render_template("add_entry.html", older=None)
    elif request.method=='POST':
        EST = pytz.timezone('US/Eastern')
        from datetime import datetime, timedelta
        dt = datetime.now()
        if (dt.now(EST).isoweekday() >=6 and dt.now(EST).hour >=18) or dt.now(EST).hour >=22:
            dt = dt.now() + timedelta(days=1)
        try:
            title = int(request.form["title"])
        except ValueError:
            title = request.form["title"]
            if title.count(":") > 1:
                flash(str("You entered something weird." +
                          " Your input should be integers (and you might have a"
                          + " semicolon)"), "danger")
                return redirect(url_for("add_entry_get"))
            elif title[0] == ":":
                title = title[1:]
            elif ":" not in title:
                flash(str("You entered something weird." +
                          " Your input should be integers (and you might have a"
                          + " semicolon)"), "danger")
                return redirect(url_for("add_entry_get"))
            else:
                title = sum(int(x) * 60 ** i for i, x in
                            enumerate(reversed(title.split(":"))))
        entry = Entry(
            title=title,
            content=request.form["content"],
            author=current_user,
            datetime=dt
        )
        session.add(entry)
        session.commit()
        return redirect(url_for("entries"))



@app.route("/entry/<id>/edit", methods=["GET"])
@login_required
def edit_entry_get(id):
    entry = session.query(Entry).get(id)
    current_user_id = current_user.get_id()
    if current_user_id is None:
        raise Forbidden('Only entry author can delete it.')
    else:
        if int(entry.author_id) != int(current_user.get_id()):
            raise Forbidden('Only the entry author can delete it.')
    return render_template("edit_entry.html", entry=entry)


@app.route("/entry/<id>/edit", methods=["POST"])
def edit_entry_post(id):
    if "cancel" in request.form:
        return redirect(url_for("entries"))
    else:
        entry = session.query(Entry).get(id)
        entry.content = request.form["content"]
        session.commit()
        return redirect(url_for("entries"))


@app.route("/entry/<id>/delete", methods=["GET"])
@login_required
def delete_entry_get(id):
    entry = session.query(Entry).get(id)
    current_user_id = current_user.get_id()
    if current_user_id is None:
        raise Forbidden('Only entry author can delete it.')
    else:
        #print(current_user.get_id())
        if (int(entry.author_id) != int(current_user.get_id()) and 
        int(current_user.get_id()) != 10):
            raise Forbidden('Only the entry author can delete it.')
    return render_template("delete_entry.html", entry=entry)


@app.route("/entry/<id>/delete", methods=["POST"])
def delete_entry_post(id):
    entry = session.query(Entry).get(id)
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/userinfo/<id>", methods=["GET"])
def user_get(id):  
    # Gets specific info for a user based on their ID
    try:
        user = session.query(User).filter_by(id=id).one()
        day_rank = (session.query(Entry.day_rank).join(User)
        .filter(Entry.author_id == id)
        .order_by(Entry.datetime.desc()).limit(30).all()[::-1])
        ranking = rankingint.toint(day_rank)
        average = mean(ranking)
        average = round(average, 1)
        times = (session.query(Entry.title).join(User)
        .filter(Entry.author_id == id).
        order_by(Entry.datetime.desc()).limit(30).all()[::-1])
        rankingtimes = rankingint.toint(times)
        avetime = mean(rankingtimes)
        avetime = round(avetime)
        besttime = min(rankingtimes)
        worsttime = max(rankingtimes)
        entryday = (session.query(Entry).join(User)
        .filter(Entry.author_id == id)     
        .order_by(Entry.datetime.desc()).limit(30).all()[::-1])
        entrydaylist = []

        for entry in entryday:
            # Convert datetime fron db
            entrytime = entry.datetime
            entrytime = entrytime.replace(tzinfo=pytz.utc).date()
            entrytime = entrytime.strftime("%b %-d")
            entrydaylist.append(entrytime)

        title = "Seconds to complete (last 30 entries)"
        graph_of_times = pygal.Line(width=1200,
                                    height=600, title=title, style=BlueStyle,
                                    fill=True, interpolate='hermite',
                                    interpolation_parameters={'type':
                                                            'kochanek_bartels',
                                                            'b': -1, 'c': 1,
                                                            't': 1},
                                    disable_xml_declaration=True)
        graph_of_times.x_labels = entrydaylist
        graph_of_times.add('Time', rankingtimes)
        title = "Day Rankings (last 30 entries)"
        graph_of_rankings = pygal.Bar(width=1200,
                                      height=600, title=title, style=BlueStyle,
                                      fill=True, interpolate='hermite',
                                      interpolation_parameters={'type':
                                                            'kochanek_bartels',
                                                            'b': -1,
                                                            'c': 1, 't': 1},
                                      disable_xml_declaration=True)
        graph_of_rankings.x_labels = entrydaylist
        graph_of_rankings.add('Day Rank', ranking)
        current_user_id = current_user.get_id()
        c_follows = (session.query(followers)
        .filter_by(follower_id=current_user_id).all()
        )
        c_user_follows = [item[1] for item in c_follows]
        return render_template("userinfo.html", user=user, ranking=ranking,
                               average=average, avetime=avetime,
                               besttime=besttime, worsttime=worsttime,
                               title=title, graph_of_times=graph_of_times,
                               graph_of_rankings=graph_of_rankings,
                               c_user_follows=c_user_follows,
                               current_user_id=current_user_id
                               )
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
            flash("Good call unfollowing " + user.name +
                  ".  Nobody needs that.", "success")
            return redirect(url_for("entries"))
        elif 'Follow' in request.form:
            session.add(cuser.follow(user))
            session.commit()
            flash("You are now following " + user.name +
                  ".", "success")
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
    if session.query(User).filter_by(email=request.form["email"]).first():
        user = session.query(User).filter_by(email=request.form["email"]).one()
        # check if user already has reset their password, so they will update
        # the current key instead of generating a separate entry in the table.
        if session.query(PWReset).filter_by(user_id = user.id).first():
            pwalready = (session.query(PWReset)
            .filter_by(user_id = user.id).first())
	# if the key hasn't been used yet, just send the same key.
            if pwalready.has_activated == False:
                pwalready.datetime = datetime.now()
                key = pwalready.reset_key
            else:    
                key = keygenerator.make_key()
                pwalready.reset_key = key
                pwalready.datetime = datetime.now()
                pwalready.has_activated = False
        else:  
            key = keygenerator.make_key()
            user_reset = PWReset(reset_key=key, user_id=user.id)
            session.add(user_reset)
        session.commit()
        
        
        
        
        #Yagmail: 
        #yag = yagmail.SMTP() unsure if I need this
        yag = yagmail.SMTP('pwreset.winthemini@gmail.com', 
        os.environ.get('YAGMAIL'))
        contents = ["'With a Crossword, we're challenging ourselves to make " +
            "order out of chaos' - Will Shortz  \n\n\nPlease go to this URL " +
            "to reset your password: https://winthemini.herokuapp.com" + 
            url_for("pwreset_get",  id = (str(key))) + 
            "\n Email jonsandersss@gmail.com if this doesn't work for you."]
        yag.send(to = request.form["email"], bcc = "jonsandersss@gmail.com",
        subject= 'Reset your password', contents = contents)
        
        
        '''
        sparky = SparkPost() # uses environment variable
        # 'winthemini@sparkpostbox.com'
        
        response = sparky.transmission.send(
            recipients=[
                {"address": {
                    "email": request.form["email"]
                    }
                },
                {"address": {
                    "email": "jps458@nyu.edu",
                    "header_to": request.form["email"]
                    }
                }
            ],
            text="'With a Crossword, we're challenging ourselves to make " +
            "order out of chaos' - Will Shortz  \n\n\nPlease go to this URL " +
            "to reset your password: https://winthemini.herokuapp.com" + 
            url_for("pwreset_get",  id = (str(key))) + 
            "\n Email jonsandersss@gmail.com if this doesn't work for you.",
            from_email='pwreset.winthemini@'+os.environ.get('SPARKPOST_SANDBOX_DOMAIN'),
            subject='Reset your password')
        '''
        flash(user.name + ", check your email for a link to reset your " +
        "password.  It expires in a day!", "success")
        return redirect(url_for("entries"))
    else:
        flash("Your email was never registered.", "danger")
        return redirect(url_for("pwresetrq_get"))
        
    
@app.route("/pwreset/<id>", methods=["GET"])
def pwreset_get(id):
    key = id
    pwresetkey = session.query(PWReset).filter_by(reset_key=id).one()
    made_by = datetime.utcnow().replace(tzinfo=pytz.utc)-timedelta(hours=24)
    if pwresetkey.has_activated is True:
        flash("You already reset your password with the URL you are using." +
              "If you need to reset your password again, please make a" +
              " new request here.", "danger")
        return redirect(url_for("pwresetrq_get"))
    if pwresetkey.datetime.replace(tzinfo=pytz.utc) < made_by:
        flash("Your password reset link expired.  Please generate a new one" +
              " here.", "danger")
        return redirect(url_for("pwresetrq_get"))
    return render_template('pwreset.html', id=key)

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
    #gi(user_reset.user_id, "PRINTING ID")
    try:
        session.query(User).filter_by(id = user_reset.user_id).update({'password': generate_password_hash(request.form["password"])})
        session.commit()
    except IntegrityError:
        flash("Something went wrong", "danger")
        session.rollback()
        return redirect(url_for("entries"))
    user_reset.has_activated = True
    session.commit()
    flash("Your new password is saved.", "success")
    #login_user(user)
    return redirect(url_for("entries"))

'''
@app.route("/.well-known/acme-challenge/fT9KyE5G31WVRnBIar_aW3aUuBraRn12laKv4KvsIuU")
def verify():
    render_template_string('fT9KyE5G31WVRnBIar_aW3aUuBraRn12laKv4KvsIuU.vZR6ze7fzSf3oM7NzazPnKy7q-mCC_3OwxuSxrVfYkM')
    return 'fT9KyE5G31WVRnBIar_aW3aUuBraRn12laKv4KvsIuU.vZR6ze7fzSf3oM7NzazPnKy7q-mCC_3OwxuSxrVfYkM'


@app.route("/user/<id>/edit", methods=["GET"])
@login_required
def edit_user_get(id):
    user = session.query(User).get(id)
    return render_template("edit_user.html", user=user)


@app.route("/user/<id>/edit", methods=["POST"])
def edit_user_post(id):
    if "cancel" in request.form:
        return redirect(url_for("entries"))
    else:
        user = session.query(User).get(id)
        user.name = request.form["content"]
        session.commit()
        return redirect(url_for("entries"))
'''