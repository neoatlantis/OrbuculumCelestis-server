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
    if isinstance(dt, pydt.datetime):
        tt = dt.utctimetuple()
    elif isinstance(dt, ephem.Date):
        tt = dt.tuple()
    else:
        raise Exception("Object cannot be converted to ISO datetime string.")
    print(tt)
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % tt 

#------------------------------------------------------------------------------

def _calcRisingSetting(observer, target):
    try:
        nextRising = strttime(observer.next_rising(target))
    except:
        nextRising = None
    try:
        nextSetting = strttime(observer.next_setting(target))
    except:
        nextSetting = None

    return (nextRising, nextSetting)


def astro(lat, lng):
    retObserver, retHeaven = {}, {} 

    # ---- Set up observer
    observer = ephem.Observer()
    observer.lat, observer.lon = str(lat), str(lng)
    observer.date = pydt.datetime.utcnow()
    retObserver = {
        "lat": lat,
        "lng": lng,
        "datetime": strttime(observer.date),
    }


    # ---- calculations for the sun
    retHeaven["sun"] = {}
    retHeaven["sun"]["rising"], retHeaven["sun"]["setting"] = \
        _calcRisingSetting(observer, ephem.Sun())

    return {
        "observer": retObserver,
        "heaven": retHeaven,
    }

###############################################################################

@route("/<lat:float>/<lng:float>/<filetype:re:(json|html){0,1}>")
def query(lat, lng, filetype):
    if not checkInput(lat, lng):
        return abort(400, "Latitude and/or longitude invalid.")
    data = astro(lat, lng)
    return json.dumps(data)
run(host="127.0.0.1", port=7778)
