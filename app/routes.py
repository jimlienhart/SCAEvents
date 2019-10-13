
from flask import render_template, flash, redirect, url_for, request

from app import app

from app.forms import EventForm

from app.event import getEvents, getEvent

@app.route('/')
@app.route('/index')
#@login_required
def index():
    events=getEvents()
    print(events)
    return render_template('index.html', title='Home', events=events)

from app.forms import MakeEventForm

@app.route('/event/<evkey>', methods=['GET', 'POST'])
#@login_required
def event(evkey):
    ev = getEvent(evkey)
    if ev:
        form = MakeEventForm(ev)
        if form.validate_on_submit():
            fname = form.firstname.data
            lname = form.lastname.data
            email = form.email.data
            print((fname,lname,email))
            return redirect(url_for('index'))
        return render_template('event.html', event=ev, form=form) 
    else:
        return redirect(url_for('index'))
        

