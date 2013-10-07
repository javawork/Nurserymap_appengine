# -*- coding:utf-8 -*-

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import os
import urllib
import re
import json
import sys
from geohash import *
from models import *
from geo.geomodel import GeoModel, geotypes

from google.appengine.api import users
from google.appengine.ext import ndb, db
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import memcache

import webapp2

class DataHandler(webapp2.RequestHandler):
	def get(self, sub_url):
		if sub_url == 'all':
			self.all()
		elif sub_url == 'query':
			area1 = self.request.get("area1")
			area2 = self.request.get("area2")
			self.query(area1, area2)
		elif sub_url == 'querydistance':
			lat = self.request.get("lat")
			lng = self.request.get("lng")
			zoom = self.request.get("zoom")
			self.querydistance(lat, lng, zoom)
		elif sub_url == 'querybox':
			north = self.request.get("north")
			east = self.request.get("east")
			south = self.request.get("south")
			west = self.request.get("west")
			result = self.request.get("result")
			self.querybox(north, east, south, west, result)
		elif sub_url == 'test':
			lat = self.request.get("lat")
			lng = self.request.get("lng")
			self.test(lat, lng)
		elif sub_url == 'count':
			self.count()
		elif sub_url == 'nursery3all':
			self.nursery3all()

	def all(self):
		qry = ndb.gql("SELECT * FROM NurseryModel")
		result = qry.fetch(2000)

		nursery_list = []
		for n in result:
			item = {}
			item['id'] = n.id;
			item['title'] = n.title;
			item['address'] = n.address;
			item['lng'] = n.lng;
			item['lat'] = n.lat;
			item['own'] = n.own;
			item['auth'] = n.auth;
			item['capacity'] = n.capacity;
			item['phone'] = n.phone;
			nursery_list.append(item)

		self.response.write( '%s'%json.dumps(nursery_list) )

	def query(self, area1, area2):
		qry = NurseryModel3.all().filter('area1 =', area1).filter('area2 =', area2)
		result = qry.fetch(2000)

		nursery_list = []
		for n in result:
			item = {}
			item['id'] = n.id;
			item['title'] = n.title;
			item['address'] = n.address;
			item['lat'] = n.location.lat + 90.0;
			item['lng'] = n.location.lon;
			item['own'] = n.own;
			item['auth'] = n.auth;
			item['capacity'] = n.capacity;
			item['phone'] = n.phone;
			nursery_list.append(item)

		self.response.write( '%s'%json.dumps(nursery_list) )

	def querydistance(self, lat, lng, zoom):
		distance = 0
		if int(zoom) < 10:
			distance = 3046.7
		elif int(zoom) < 14:
			distance = 2046.7
		elif int(zoom) < 18:
			distance = 1046.7
		else:
			distance = 804.7

		lat_f = float(lat) - 90.0
		lng_f = float(lng)
		results = NurseryModel2.proximity_fetch(
			NurseryModel2.all(),  # Rich query!
			geotypes.Point(lat_f, lng_f),  # Or db.GeoPt
			max_results=1000,
			max_distance=distance)  # Within 50 miles.

		nursery_list = []
		for n in results:
			item = {}
			item['id'] = n.id;
			item['title'] = n.title;
			item['address'] = n.address;
			item['lat'] = n.location.lat + 90.0;
			item['lng'] = n.location.lon;
			item['own'] = n.own;
			item['auth'] = n.auth;
			item['capacity'] = n.capacity;
			item['phone'] = n.phone;
			nursery_list.append(item)
			#self.response.write('%s %s<br/>'%(n.address, str(n.location) ))

		self.response.write( '%s'%json.dumps(nursery_list) )

	def querybox(self, north, east, south, west, result):
		results = NurseryModel3.bounding_box_fetch(
			NurseryModel3.all(),  # Rich query!
			geotypes.Box(float(north)-90.0, float(east), float(south)-90.0, float(west)),
			#geotypes.Box(lat_f+delta, lng_f+delta, lat_f-delta, lng_f-delta),
			max_results=int(result))

		nursery_list = []
		for n in results:
			item = {}
			item['id'] = n.id;
			item['title'] = n.title;
			item['address'] = n.address;
			item['lat'] = n.location.lat + 90.0;
			item['lng'] = n.location.lon;
			item['own'] = n.own;
			item['auth'] = n.auth;
			item['capacity'] = n.capacity;
			item['phone'] = n.phone;
			nursery_list.append(item)
			#self.response.write('%s %s<br/>'%(n.address, str(n.location) ))

		self.response.write( '%s'%json.dumps(nursery_list) )

	def count(self):
		nursery_count = NurseryModel.query().count()
		self.response.write( 'Nursery = %d<br/>'%(nursery_count))

		nursery2_result = NurseryModel2.all(keys_only = True).fetch(999999)
		self.response.write( 'Nursery2 = %d<br/>'%(len(nursery2_result)))

		nursery3_result = NurseryModel3.all(keys_only = True).fetch(999999)
		self.response.write( 'Nursery3 = %d<br/>'%(len(nursery3_result)))

		offset3 = getoffset3()
		self.response.write( 'Offset = %d<br/>'%(offset3))

		page_count_total = PageModel.query().count(999999)
		page_count_gt0 = PageModel.query(PageModel.count > 0).count(999999)
		self.response.write( 'Page = %d / %d<br/>'%(page_count_gt0, page_count_total) )

	def nursery3all(self):
		nursery3_result = NurseryModel3.all().fetch(999999)
		for n in nursery3_result:
			self.response.write('%s %s<br/>'%(n.id, n.title))

	def test(self, lat, lng):
		model = NurseryModel4(
			location=ndb.GeoPt(float(lng)-90.0, float(lat)),
			id = '11119999' )
		model.update_location()
		model.put()	

