#! /usr/bin/python3

import json
import sys
from glob import glob
from datetime import date

import traceback, pdb
def debug(tp, val, tb):
    traceback.print_exception(tp, val, tb)
    pdb.pm()
sys.excepthook = debug

def _jsonget_(js, key, default=''):
    try:
        return js[key]
    except:
        return default

def __key__(name):
    return name.replace(' ','_').lower()
    
class Version:
    def __init__(self, s=''):
        self.major = 0
        self.minor = 0
        if s:
            self.major, self.minor = map(int, s.split('.'))
    def __repr__(self):
        return '{0}.{1}'.format(self.major,self.minor)
    def __bool__(self):
        return self.major > 0 or self.minor > 0

class Staff:
    def __init__(self, st={}):
        self.title = _jsonget_(st,'title')
        self.names = _jsonget_(st,'names')
    def __repr__(self):
        return self.title + ' : ' + str(self.names)
    def __bool__(self):
        return self.title != ''
    
class FeeCategory:
    def __init__(self, fc):
        self.name = _jsonget_(fc, 'name')
        self.key = __key__(self.name)
        self.desc = _jsonget_(fc, 'desc')
        self.nms = int(_jsonget_(fc, 'nms', 0.0) * 100)
    def Option(self):
        return {self.key, str(self)}
    def __str__(self):
        fc = self.name
        if self.desc:
            fc += ' (' + self.desc + ')'
        return fc
    def __repr__(self):
        fc = self.name
        if self.desc:
            fc += ' (' + self.desc + ')'
        fc += ' : ' + str(self.nms)
        return fc
    def __bool__(self):
        return self.name != ''
    
class Fee:
    def __init__(self, fee):
        self.name = _jsonget_(fee, 'name')
        self.key = __key__(self.name)
        self.fees = _jsonget_(fee, 'fees', [])
        for f in self.fees:
            self.fees[f] = self.fees[f] * 100
    def __repr__(self):
        return self.name + ' : ' + str(self.fees)
    def __bool__(self):
        return self.fee != ''

class Comp:
    def __init__(self, f):
        self.name = _jsonget_(f, 'name')
        self.key = __key__(self.name)
        self.family = _jsonget_(f, 'family', False)
        
def KeyDict(f):
    d = {}
    for x in f:
        d[x.key] = x
    return d

class Event:
    def __init__(self, f=None):
        try:
            js = json.load(open(f,'r'))
        except:
            js = None
        self.version = Version(_jsonget_(js, 'version'))
        self.key = _jsonget_(js, 'key')
        self.event = _jsonget_(js, 'event')
        self.dates = [date.fromisoformat(d) for d in _jsonget_(js, 'dates', {})]
        self.site = _jsonget_(js, 'site')
        self.address = _jsonget_(js, 'address')
        self.staff = [Staff(s) for s in _jsonget_(js,'staff', {})]
        self.feeClasses = [FeeCategory(fc) for fc in _jsonget_(js, 'feeClasses', {})]
        self.feeClassDict = KeyDict(self.feeClasses)
        self.fees = [Fee(f) for f in _jsonget_(js, 'fees', {})]
        self.comp = [Comp(f) for f in _jsonget_(js, 'comp', {})]
        self.admission =  [Fee(f) for f in _jsonget_(js, 'admission', {})]
        self.feeDict = {}
        for f in self.admission:
            self.feeDict[f.key] = {'name' : f.name, 'fees' : f.fees }
        for f in self.fees:
            self.feeDict[f.key] = {'name' : f.name, 'fees' : f.fees }
        self.nadmcols = len(self.admission)
        self.label = self.event
        self.sortkey = date(1900,1,1)
        if len(self.dates) > 0:
            self.sortkey = self.dates[0]
            self.label += ' : ' + self.dates[0].strftime('%x')
            if len(self.dates) > 1:
                self.label += '-' + self.dates[1].strftime('%x')
        self.autocrat = '???'
        self.totalCol = 6 + len(self.feeDict)
        self.numNameCols = 6
        self.numAdmCols = len(self.admission)
        self.numFeeCols = len(self.fees)
        if self.numAdmCols > 1:
            self.admLabel = 'Admission'
        else:
            self.admLabel = ''
        self.admkeys = [f.key for f in self.admission]
        self.special = ''
        sep = ''
        for c in self.comp:
            self.special += sep + c.name
            sep = ',<br/>'
        self.scripts = ''

        self.scripts += """
function isAttending(idx) {
     return """
        sep = ''
        for f in self.admission:
            self.scripts += sep + 'isResvFieldChecked(idx,"' + f.key + '")'
            sep += ' || '
        self.scripts += """;
}
"""
        self.scripts += """
function checkAdmission(idx, key) {
    admKeys = ["""
        sep = ''
        for k in self.admkeys:
            self.scripts += sep + '"' + k + '"'
            sep = ','
        self.scripts += """];
    if (admKeys.indexOf(key) >= 0) {
        for (k in admKeys) {
            if (admKeys[k] != key) {
                setResvFieldChecked(idx, admKeys[k], false);
            }
        }
    }
}
"""
        self.scripts += """
function getFeeTable() {
    fees = {}"""
        for fc in self.feeClasses:
            self.scripts += """
    fees["%s"] = {"nms" : %0.2f};""" % (fc.key, fc.nms)
            for f in self.feeDict:
                try:
                    fee = self.feeDict[f]["fees"][fc.name]
                except:
                    fee = self.feeDict[f]["fees"]["*"]
                self.scripts += """
    fees["%s"]["%s"] = %0.2f;""" % (fc.key,f,fee)
        self.scripts += """
    return fees;
}
"""
        self.scripts += """
function calcRowTotal(idx) {
    var total = 0.0;
    var attend = isAttending(idx);
    if (attend) {
        age = getResvFieldValue(idx, "age");
        if (isFieldEmpty(idx, "membernumber")) {
            total += FEES[age]["nms"];
        }"""
        for f in self.feeDict:
            self.scripts += """
        if (isResvFieldChecked(idx, "%s")) {
            total += FEES[age]["%s"];
        }""" % (f,f)
        self.scripts += """
    }
    setResvTotal(idx, total);
    return total;
}
"""
        
EVENTS = {}
for f in glob('events/*.json'):
    ev = Event(f)
    if ev:
        EVENTS[ev.key] = ev

def getEvents():
    events = list(EVENTS.values())
    events.sort(key=lambda event : event.sortkey)
    return events

def getEvent(key):
    try:
        return EVENTS[key]
    except:
        return None

if __name__ == '__main__':
    for ev in getEvents():
        ev.prt()
