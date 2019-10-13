from flask_wtf import FlaskForm
from wtforms import Form, FormField, FieldList
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms import TextAreaField, SubmitField, SelectField, IntegerField
from wtforms import Field
from wtforms.widgets import TextInput
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.validators import ValidationError, Email, EqualTo, Optional

import json

class ResvLine(Form):
    firstname = StringField('First Name', [Optional()])
    lastname = StringField('Last Name', [Optional()])
    scaname = StringField('SCA Name', [Optional()])
    membernumber = IntegerField('Member Number', [Optional(), NumberRange(1,10000000)])
    family = BooleanField('Family')
    age = SelectField("Age", [Optional()], choices=[
        ('adult', 'Adult'),
        ('youth', 'Youth (6-17)'),
        ('child', 'Child (0-5)')])
    total = StringField('Total', render_kw={'readonly': True})

class EventForm(FlaskForm):
    email = StringField('EMail', [Email(),DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    phone = StringField('Phone (optional)', [Optional()])
    firstname = StringField('First Name', [DataRequired()])
    lastname = StringField('Last Name', [DataRequired()])
    scaname = StringField('SCA Name', [Optional()])
    membernumber = IntegerField('Member Number', [Optional])
    address = TextAreaField('Address', [Optional])    
    reservations = None
    total = StringField('Total Due', render_kw={'readonly': True})
    submit = SubmitField('Submit')


def MakeEventForm(ev):
    admfields = {}
    feefields = {}
    rsvl = type(ev.key+'ResvLine', (ResvLine,), {})
    for f in ev.admission:
        setattr(rsvl, f.key, BooleanField(f.name))
        admfields[f.key] = f.name
    for f in ev.fees:
        setattr(rsvl, f.key, BooleanField(f.name))
        feefields[f.key] = f.name
    if ev.comp:
        speclabel = 'Special<br/>Select if you are:'
        specchoices = [('','')]
        for c in ev.comp:
            speclabel += '<br/>' + c.name
            specchoices.append((c.key, c.name))
        setattr(rsvl, 'special', SelectField(speclabel, [Optional()], choices=specchoices))
    evf = type(ev.key+'EventForm', (EventForm,), {
        'reservations': FieldList(FormField(rsvl), min_entries=16, max_entries=16),
        'admfields' : admfields,
        'feefields' : feefields
        })
    return evf(fees=json.dumps(ev.feeDict))
