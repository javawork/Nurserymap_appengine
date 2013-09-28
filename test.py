# -*- coding:utf-8 -*-

import cgi
import os
import urllib
import re
import json
from geohash import *
import math

def getdistance(a, b):
	x = Geohash(a).point()[0] - Geohash(b).point()[0]
	y = Geohash(a).point()[1] - Geohash(b).point()[1]
	return math.sqrt(x*x + y*y)

lng = 37.5387583158
lat  = 127.208374114
#gh1 = Geohash( data=(lng,lat), bound=(-180,-80,180,80), depth=32 )
gh1 = Geohash( (lat, lng) )
gh2 = Geohash( (lat+1, lng+1) )
print str(gh1), gh1.bbox()
print str(gh2), gh2.bbox()
#print gh1.point(), gh2.point()
#print math.sqrt(0.1)
#print getdistance(str(gh1), str(gh2))
gh0 = gh1+gh2
print str(gh0), (gh0).bbox()