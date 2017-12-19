#!/usr/bin/env python3

"""
Server for Astronomical Calculations
====================================

after firing up, visit:
    http://localhost:7778/<latitude>/<longitude>/json, or
    http://localhost:7778/<latitude>/<longitude>/html(currently under dev)
for data.

Notice: the begin/end of twilight, as well as sun/other celestial bodies' rise
and set, are calculated for the most nearst time in the future. That means,
depending on currently the given location is in day or night, either time can
come earlier than the other. In daytime the sunset time is the time for that
day, and the sunrise time comes after that.
"""

import sys
import json
import yaml
import datetime as pydt

from bottle import *
import ephem

from _timezone import googleTimezone
from _verifyLatLng import verifyLatLng

###############################################################################

def strttime(dt):
    if isinstance(dt, pydt.datetime):
        tt = dt.utctimetuple()
    elif isinstance(dt, ephem.Date):
        tt = dt.tuple()
    else:
        raise Exception("Object cannot be converted to ISO datetime string.")
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % tt 

#------------------------------------------------------------------------------

def _calcRisingSetting(observer, target, horizon=0, use_center=False):
    observer.horizon = str(horizon) 
    try:
        nextRisingTime = observer.next_rising(target, use_center=use_center)
        nextRising = strttime(nextRisingTime)
    except:
        nextRising = None
    try:
        nextSettingTime = observer.next_setting(target, use_center=use_center)
        nextSetting = strttime(nextSettingTime)
    except:
        nextSetting = None
    return (nextRising, nextSetting)

def _calcTwilight(observer):
    sun = ephem.Sun()
    civil = _calcRisingSetting(observer, sun, -6, True)
    nautical = _calcRisingSetting(observer, sun, -12, True)
    astronomical = _calcRisingSetting(observer, sun, -18, True)
    breakdown = lambda i: {"begin": i[0], "end": i[1]}
    return {
        "civil": breakdown(civil),
        "nautical": breakdown(nautical),
        "astronomical": breakdown(astronomical),
    }



def astro(lat, lng, pressureFix=None, temperatureFix=None, timezoneInfo=None):
    retObserver, retHeaven = {}, {} 

    # ---- Set up observer
    observer = ephem.Observer()
    observer.lat, observer.lon = str(lat), str(lng)
    observer.date = pydt.datetime.utcnow()
    retObserver = {
        "lat": lat,
        "lng": lng,
        "datetime": strttime(observer.date),
        "twilight": _calcTwilight(observer), 
    }
    if pressureFix:
        retObserver["pressure"] = pressureFix
        observer.pressure = pressureFix / 1000.0
    if temperatureFix:
        retObserver["temperature"] = temperatureFix
        observer.temp = temperatureFix - 273.15
    retObserver["timezone"] = timezoneInfo

    # ---- calculations for a few celestial bodies
    bodies = {"sun": ephem.Sun, "moon": ephem.Moon}
    for i in bodies:
        retHeaven[i] = {}
        retHeaven[i]["rising"], retHeaven[i]["setting"] = \
            _calcRisingSetting(observer, bodies[i]())

    return {
        "observer": retObserver,
        "heaven": retHeaven,
    }

###############################################################################

# ---- Read config file
GOOGLE_TIMEZONE_TOKEN = None 
try:
    config = yaml.load(open(sys.argv[1], 'r').read())
    GOOGLE_TIMEZONE_TOKEN = config["google-timezone-api"]
except Exception(e):
    print("Warning: Cannot load google timezone api. Set up config.yaml properly.")



@route("/<lat:float>/<lng:float>/<filetype:re:(json|html){0,1}>")
def query(lat, lng, filetype):
    if not verifyLatLng(lat, lng):
        return abort(400, "Latitude and/or longitude invalid.")
    params = request.query
    try:
        pressureFix = float(params["pressure"])      # in Pascal
        assert pressureFix > 10000 and pressureFix < 120000
    except:
        pressureFix = None
    try:
        temperatureFix = float(params["temperature"]) # in Kelvin
        assert temperatureFix > 150 and temperatureFix < 373
    except:
        temperatureFix = None

    timezoneInfo = googleTimezone(GOOGLE_TIMEZONE_TOKEN, lat, lng)

    data = astro(\
        lat,
        lng,
        temperatureFix=temperatureFix,
        pressureFix=pressureFix,
        timezoneInfo=timezoneInfo,
    )
    return json.dumps(data)
run(host="127.0.0.1", port=7778)
