#!/usr/bin/env python3

import json
import datetime as pydt

from bottle import *
import ephem

###############################################################################

def checkInput(lat, lng):
    try:    
        assert type(lat) == float
        assert type(lng) == float
        if lat > 90 or lat < -90: return False
        if lng <= -180 or lng > 180: return False
    except:
        return False
    return True

def strttime(dt):
    return "%d/%d/%d %d:%d:%d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def datetimeToISOString(dt):
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

#------------------------------------------------------------------------------

def _calcRisingSetting(observer, target):
    try:
        nextRising = observer.next_rising(target)
    except:
        nextRising = None
    try:
        nextSetting = observer.next_setting(target)
    except:
        nextSetting = None

    return (
        datetimeToISOString(ephem.localtime(nextRising)),
        datetimeToISOString(ephem.localtime(nextSetting))
    )


def astro(lat, lng):
    ret = {}

    # ---- Set up observer
    observer = ephem.Observer()
    observer.lat, observer.lon = str(lat), str(lng)
    observer.date = pydt.datetime.utcnow()

    # ---- calculations for the sun
    ret["sun"] = {}
    ret["sun"]["rising"], ret["sun"]["setting"] = \
        _calcRisingSetting(observer, ephem.Sun())

    return ret

###############################################################################

@route("/<lat:float>/<lng:float>/<filetype:re:(json|html){0,1}>")
def query(lat, lng, filetype):
    if not checkInput(lat, lng):
        return abort(400, "Latitude and/or longitude invalid.")
    data = astro(lat, lng)
    return json.dumps(data)
run(host="127.0.0.1", port=7778)
