#!/usr/bin/env python3

import datetime
import requests

def googleTimezone(token, lat, lng, timeout=30):
    try:
        assert type(token) == str and token != ''
        latlngStr = "%.3f,%.3f" % (lat, lng)
        timestamp = int(datetime.datetime.utcnow().timestamp())
        url = "https://maps.googleapis.com/maps/api/timezone/json?"
        url += "location=%s&timestamp=%d&key=%s" % (latlngStr, timestamp, token)
        
        q = requests.get(url, timeout=timeout)
        ret = q.json()
        assert 'dstOffset' in ret and type(ret['dstOffset']) in [float, int]
        assert 'rawOffset' in ret and type(ret['rawOffset']) in [float, int]
        assert 'timeZoneId' in ret and type(ret['timeZoneId']) == str
        assert 'timeZoneName' in ret and type(ret['timeZoneName']) == str
        return ret
    except Exception as e:
        return {
            'status': 'default',
            'dstOffset': 0,
            'rawOffset': 0,
            'timeZoneId': 'Etc/UTC',
            'timeZoneName': 'Coordinated Universal Time',
        } 
