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
from geo.geomodel import GeoModel, geotypes

from google.appengine.api import users
from google.appengine.ext import ndb, db
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import memcache

import webapp2

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

def get_between_str(str, start, end):
	pos1 = str.find(start)
	if pos1 == -1:
		return ''
	
	pos1 = pos1 + len(start)
	pos2 = str[pos1:].find(end)
	return str[pos1:pos1+pos2]

def fetch_nursery_list_content(offset, area1, area2):
		url = "http://placardmart.com/lab/childcare_list?offset=%d&area1=%s&area2=%s"%(offset, area1, area2)
		result = urlfetch.fetch(url=url,
		    method=urlfetch.GET,
		    headers={'Content-Type': 'application/x-www-form-urlencoded'},
	    	deadline=60
	    )

		if result.status_code <> 200:
			return ''
		else:
			return result.content

def fetch_nursery_detail_content(id):
		url = "http://placardmart.com/lab/childcare_detail?id=%s"%(id)
		result = urlfetch.fetch(url=url,
		    method=urlfetch.GET,
		    headers={'Content-Type': 'application/x-www-form-urlencoded'},
	    	deadline=60
	    )

		if result.status_code <> 200:
			return ''
		else:
			return result.content			

def fetch_nursery_map_content(id):
		url = "http://placardmart.com/lab/childcare_map?id=%s"%(id)
		result = urlfetch.fetch(url=url,
		    method=urlfetch.GET,
		    headers={'Content-Type': 'application/x-www-form-urlencoded'},
	    	deadline=60
	    )

		if result.status_code <> 200:
			return ''
		else:
			return result.content			

def get_one_nursery_string(total, cur_pos):
	pos1 = total[cur_pos:].find('onclick="goClubMain(')
	if pos1 == -1:
		return 0, 0
		
	pos2 = total[cur_pos+pos1:].find('<img')

	start = cur_pos+pos1
	end = cur_pos+pos1+pos2
	return start, end

def get_id(str):
	id = get_between_str(str, "goClubMain('", "'")
	return id		

def get_detail(str):
	title = get_between_str(str, '<th scope="row">어린이집명</th>', '</td>')
	title = title.replace('<td>', '')
	title = title.strip()

	address= get_between_str(str, '<th scope="row">주소</th>', '</td>')
	address = address.replace('<td colspan="3">', '')
	pos = address.find(']')
	if pos <> -1:
		address = address[pos+1:]

	address = address.replace(get_between_str(address, '(', ')'), '')
	address = address.replace('(', '').replace(')', '')
	address = address.strip()

	own = get_between_str(str, '<th scope="row">어린이집유형</th>', '</td>')
	own = own.replace('<td>', '')
	own = own.strip()

	auth = get_between_str(str, '<th scope="row">어린이집평가인증</th>', '</td>')
	auth = auth.replace('<td>', '')
	auth = auth.strip()

	capacity = get_between_str(str, '<th>정원</th>', '</td>')
	capacity = capacity.replace('<td>', '')
	capacity = capacity.replace(get_between_str(capacity, '(', ')'), '')
	capacity = capacity.replace('(', '').replace(')', '')
	capacity = capacity.strip()

	phone = get_between_str(str, '1.전화번호 : ', '<br />')
	phone = phone.strip()

	return title, address, own, auth, capacity, phone

def get_position(str):
	latlng_str = get_between_str(str, 'center: new daum.maps.LatLng(', ')')
	latlng_array = latlng_str.split(',')
	if len(latlng_array) < 2:
		return '', ''

	return latlng_array[0].strip(), latlng_array[1].strip()	

class NurseryModel(ndb.Model):
	id = ndb.StringProperty()
	title = ndb.StringProperty()
	address = ndb.StringProperty()
	lng = ndb.FloatProperty()
	lat = ndb.FloatProperty()
	own = ndb.StringProperty()
	auth = ndb.StringProperty()
	capacity = ndb.StringProperty()
	phone = ndb.StringProperty()
	area1 = ndb.StringProperty()
	area2 = ndb.StringProperty()

	@classmethod
	def query_nursery(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.id)

class AreaCode(ndb.Model):
	area1 = ndb.StringProperty()
	area2 = ndb.StringProperty()
	page = ndb.IntegerProperty()
	desc = ndb.StringProperty()

class PageModel(ndb.Model):
	offset = ndb.IntegerProperty()
	area1 = ndb.StringProperty()
	area2 = ndb.StringProperty()
	count = ndb.IntegerProperty()

class NurseryModel2(GeoModel):
	id = db.StringProperty()
	title = db.StringProperty()
	address = db.StringProperty()
	own = db.StringProperty()
	auth = db.StringProperty()
	capacity = db.StringProperty()
	phone = db.StringProperty()
	area1 = db.StringProperty()
	area2 = db.StringProperty()

class NurseryModel3(GeoModel):
	id = db.StringProperty()
	title = db.StringProperty()
	address = db.StringProperty()
	own = db.StringProperty()
	auth = db.StringProperty()
	capacity = db.StringProperty()
	phone = db.StringProperty()
	area1 = db.StringProperty()
	area2 = db.StringProperty()

class OffsetModel(ndb.Model):
	offset3 = ndb.IntegerProperty()

def get_page_data():
	qry = ndb.gql("SELECT * FROM PageModel WHERE count = 0")
	result = qry.fetch(100)

	for n in result:
		#n.count = 1
		k = n.put()
		return k.urlsafe(), n.offset, n.area1, n.area2

	return '', -1, '', ''

def get_area_data():
	qry = ndb.gql("SELECT * FROM AreaCode WHERE page = 0")
	result = qry.fetch(10)

	for n in result:
		k = n.put()
		return k.urlsafe(), n.area1, n.area2

	return '', '', ''	

def insert_nursery(id, title, address, lng_str, lat_str, own, auth, capacity, phone, area1, area2):
	try:
		lng_float = float(lng_str)
		lat_float = float(lat_str)

		model = NurseryModel(
			parent=ndb.Key('nursery', '*notitle*'),
			id = id,
			title = title,
			address = address,
			lng = lng_float,
			lat = lat_float,
			own = own,
			auth = auth,
			capacity = capacity,
			phone = phone,
			area1 = area1,
			area2 = area2 )
		model.put()
	except:
		return False

	return True

def insert_nursery2(n):
	model = NurseryModel2(
		location=ndb.GeoPt(n.lat-90.0, n.lng),
		id = n.id,
		title = n.title,
		address = n.address,
		own = n.own,
		auth = n.auth,
		capacity = n.capacity,
		phone = n.phone,
		area1 = n.area1,
		area2 = n.area2 )
	model.update_location()
	model.put()
	return True

def insert_nursery3(n):
	model = NurseryModel3(
		location=ndb.GeoPt(n.lat-90.0, n.lng),
		id = n.id,
		title = n.title,
		address = n.address,
		own = n.own,
		auth = n.auth,
		capacity = n.capacity,
		phone = n.phone,
		area1 = n.area1,
		area2 = n.area2 )
	model.update_location()
	model.put()
	return True

def update_area(area1, area2, desc):
	qry = ndb.gql("SELECT * FROM AreaCode WHERE area1='%s' AND area2='%s'"%(area1, area2))
	result = qry.fetch(1)
	if len(result) == 0:
		return False

	k = result[0].put()
	urlString = k.urlsafe()

	rev_key = ndb.Key(urlsafe=urlString)
	model = rev_key.get()
	model.desc = desc
	model.put()
	return True

def insert_area(area1, area2, desc):
	model = AreaCode(
		parent=ndb.Key("area", '*notitle*'),
			area1 = area1,
			area2 = area2,
			page = 0,
			desc = desc
		)
	model.put()

def update_rect(area1, area2, minLng, minLat, maxLng, maxLat, centerLng, centerLat):
	qry = ndb.gql("SELECT * FROM RectModel WHERE area1='%s' AND area2='%s'"%(area1, area2))
	result = qry.fetch(1)
	if len(result) == 0:
		return False

	k = result[0].put()
	urlString = k.urlsafe()

	lat = float(centerLat)
	if lat > 90:
		lat = lat - 90
	elif lat < -90:
		lat = lat + 90

	lng = float(centerLng)
	if lng > 180:
		lng = lng - 180
	elif lng < -180:
		lng = lng + 180

	rev_key = ndb.Key(urlsafe=urlString)
	model = rev_key.get()
	model.minLng = float(minLng)
	model.minLat = float(minLat)
	model.maxLng = float(maxLng)
	model.maxLat = float(maxLat)
	model.centerLng = float(centerLng)
	model.centerLat = float(centerLat)
	model.geoHash = str(Geohash((model.centerLat, model.centerLng)))
	model.geopt = ndb.GeoPt(lat, lng)
	model.put()
	return True

def insert_rect(area1, area2, minLng, minLat, maxLng, maxLat, centerLng, centerLat):
	lat = float(centerLat)
	if lat > 90:
		lat = lat - 90
	elif lat < -90:
		lat = lat + 90

	lng = float(centerLng)
	if lng > 180:
		lng = lng - 180
	elif lng < -180:
		lng = lng + 180

	model = RectModel(
		parent=ndb.Key("rect", '*notitle*'),
			area1 = area1,
			area2 = area2,
			minLng = float(minLng),
			minLat = float(minLat),
			maxLng = float(maxLng),
			maxLat = float(maxLat),
			centerLng = float(centerLng),
			centerLat = float(centerLat),
			geoHash = str(Geohash((float(centerLat), float(centerLng)))),
			geopt = ndb.GeoPt(lat, lng)
		)
	model.put()

def insert_page(offset, area1, area2):
	model = PageModel(
		parent=ndb.Key("page", '*notitle*'),
			offset = offset,
			area1 = area1,
			area2 = area2,
			count = 0
	)
	model.put()

def save_areacode_page(urlString, page):
	rev_key = ndb.Key(urlsafe=urlString)
	model = rev_key.get()
	model.page = page
	model.put()

def save_page_count(urlString, count):
	rev_key = ndb.Key(urlsafe=urlString)
	model = rev_key.get()
	model.count = count
	model.put()

def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def getoffset3():
	qry = OffsetModel.query()
	result = qry.fetch(1)
	if len(result) == 0:
		return 0

	return result[0].offset3

def setoffset3(offset):
	qry = OffsetModel.query()
	result = qry.fetch(1)
	offsetModel = result[0]
	k = offsetModel.put()
	urlString = k.urlsafe()

	rev_key = ndb.Key(urlsafe=urlString)
	model = rev_key.get()
	model.offset3 = offset
	model.put()

class CollectHandler(webapp2.RequestHandler):
	def get(self, sub_url):
		if sub_url == 'detail':
			self.detail()
		elif sub_url == 'list':
			self.list()
		elif sub_url == 'viewarea':
			self.viewarea()
		elif sub_url == 'viewpage':
			self.viewpage()
		elif sub_url == 'addarea':
			self.addarea()
		elif sub_url == 'addarea_do':
			self.addarea_do()
		elif sub_url == 'addpage':
			self.addpage()
		elif sub_url == 'delpage':
			self.delpage()
		elif sub_url == 'remainpage':
			self.remainpage()
		elif sub_url == 'remainarea':
			self.remainarea()
		elif sub_url == 'delnursery':
			self.delnursery()
		elif sub_url == 'addrect':
			self.addrect()
		elif sub_url == 'addnursery2':
			self.addnursery2()
		elif sub_url == 'addnursery3':
			self.addnursery3()

	def addnursery3(self):
		offset = getoffset3()

		fetch_count = 10
		qry = NurseryModel.query().order(NurseryModel.id)
		result = qry.fetch(fetch_count, offset = offset)

		for n in result:
			self.response.write('%s<br/>'%n.id)
			if insert_nursery3(n):
				offset = offset + 1

		setoffset3(offset)

	def addnursery2(self):
		offset_key = 'geopt:offset'
		offset = memcache.get(offset_key)

		if offset == None:
			offset = 0

		fetch_count = 100
		qry = NurseryModel.query().order(NurseryModel.id)
		result = qry.fetch(fetch_count, offset = offset)

		for n in result:
			self.response.write('%s<br/>'%n.id)
			if insert_nursery2(n):
				offset = offset + 1

		memcache.set(offset_key, offset)

	def addarea(self):
		self.response.write('<form name="input" action="addarea_do" method="get">')
		self.response.write('area1: <input type="text" name="area1"><br/>')
		self.response.write('area2: <input type="text" name="area2"><br/>')
		self.response.write('desc: <input type="text" name="desc"><br/>')
		self.response.write('<input type="submit" value="Submit"></form>');

	def addarea_do(self):
		area1 = self.request.get("area1")
		area2 = self.request.get("area2")
		desc = self.request.get("desc")
		self.response.write('%s, %s, %s<br/>'%(area1, area2, desc))

		if update_area(area1, area2, desc):
			self.response.write('updated.')			
		else:
			insert_area(area1, area2, desc)
			self.response.write('inserted.')

	def addpage(self):
		offset = self.request.get("offset")
		area1 = self.request.get("area1")
		area2 = self.request.get("area2")
		insert_page(int(offset), area1, area2)

	def addrect(self):
		area1 = self.request.get("area1")
		area2 = self.request.get("area2")
		minLng = self.request.get("minLng")
		minLat = self.request.get("minLat")
		maxLng = self.request.get("maxLng")
		maxLat = self.request.get("maxLat")
		centerLng = self.request.get("centerLng")
		centerLat = self.request.get("centerLat")
		#self.response.write('%s, %s, %s<br/>'%(area1, area2, desc))

		if not update_rect(area1, area2, minLng, minLat, maxLng, maxLat, centerLng, centerLat):
			insert_rect(area1, area2, minLng, minLat, maxLng, maxLat, centerLng, centerLat)

	def delpage(self):
		pass
		#qry = ndb.gql("SELECT * FROM PageModel")		
		#ndb.delete_multi(qry.fetch(999999, keys_only=True))

	def delnursery(self):
		pass
		#qry = ndb.gql("SELECT * FROM NurseryModel")		
		#ndb.delete_multi(qry.fetch(999999, keys_only=True))

	def viewarea(self):
		qry = ndb.gql("SELECT * FROM AreaCode")
		result = qry.fetch(100)
		for n in result:
			self.response.write('%s %s %d <br/>'%(n.area1, n.area2, n.page))

	def viewpage(self):
		qry = ndb.gql("SELECT * FROM PageModel")
		result = qry.fetch(100)
		for n in result:
			self.response.write('%d %s %s %d <br/>'%(n.offset, n.area1, n.area2, n.count))

	def remainarea(self):
		qry = ndb.gql("SELECT * FROM AreaCode WHERE page = 0")
		result = qry.fetch(999999)
		self.response.write('%d<br/>'%len(result) )

	def remainpage(self):
		qry = ndb.gql("SELECT * FROM PageModel WHERE count = 0")
		result = qry.fetch(999999)
		self.response.write('%d<br/>'%len(result) )

	def list(self):
		urlString, area1, area2 = get_area_data()
		if urlString == '':
			self.response.write('nothing')
			return

		self.response.write( '%s %s<br/><br/>'%(area1, area2))
		page = 0
		offset = 0
		total_count = 0
		while(True):
			whole_str = fetch_nursery_list_content(offset, area1, area2)
			cur_pos = 0
			local_count = 0
			while(True):
				start, end = get_one_nursery_string(whole_str, cur_pos)
				if start == 0:
					break

				cur_pos = end

				cur_str = whole_str[start:end]
				id = get_id(cur_str)

				if not RepresentsInt(id):
					continue

				if int(id) < 10000:
					continue

				self.response.write('%s %d<br/>'%(id, cur_pos))
				local_count = local_count + 1

			if local_count == 0:
				break

			if offset > 5000:
				break

			self.response.write('%d %d<br/>'%(offset, local_count))
			insert_page(offset, area1, area2)
			total_count = total_count + local_count
			page = page + 1
			offset = offset + 10

		self.response.write( 'total_count = %d, page = %d<br/><br/>'%(total_count, page))
		save_areacode_page(urlString, page)


	def detail(self):
		urlString, offset, area1, area2 = get_page_data()
		if urlString == '':
			self.response.write('nothing')
			return

		self.response.write( '%d %s %s<br/>'%(offset, area1, area2))		

		whole_str = fetch_nursery_list_content(offset, area1, area2)
		count = 0
		cur_pos = 0
		while(True):
			start, end = get_one_nursery_string(whole_str, cur_pos)
			if start == 0:
				break

			cur_pos = end

			cur_str = whole_str[start:end]
			id = get_id(cur_str)

			detail_content = fetch_nursery_detail_content(id)
			title, address, own, auth, capacity, phone = get_detail(detail_content)
			if not title:
				continue

			map_content = fetch_nursery_map_content(id)
			lat, lng = get_position(map_content)
			if not lat:
				continue

			self.response.write('%s %s %s %s %s<br/>'%(id, title, address, lat, lng))
			self.response.write('%s %s %s %s<br/>'%(own, auth, capacity, phone))
			if insert_nursery(id, title, address, lat, lng, own, auth, capacity, phone, area1, area2):
				count = count + 1
			
		self.response.write('count = %d<br/>'%count)
		save_page_count(urlString, count)

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
			lat = self.request.get("lat")
			lng = self.request.get("lng")
			zoom = self.request.get("zoom")
			self.querybox(lat, lng, zoom)
		elif sub_url == 'test':
			self.test()
		elif sub_url == 'count':
			self.count()


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
		qry = ndb.gql("SELECT * FROM NurseryModel WHERE area1='%s' AND area2='%s'"%(area1, area2))
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

	def querybox(self, lat, lng, zoom):
		delta = 0.0
		if int(zoom) <= 10:
			delta = 0.05
		elif int(zoom) <= 12:
			delta = 0.025
		elif int(zoom) <= 14:
			delta = 0.01
		elif int(zoom) <= 16:
			delta = 0.005
		elif int(zoom) <= 18:
			delta = 0.0025
		else:
			delta = 0.001

		lat_f = float(lat) - 90.0
		lng_f = float(lng)
		results = NurseryModel2.bounding_box_fetch(
			NurseryModel2.all(),  # Rich query!
			geotypes.Box(lat_f+delta, lng_f+delta, lat_f-delta, lng_f-delta),
			max_results=1000)

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

		#nursery_count3 = ndb.gql("SELECT * FROM NurseryModel3").count()		
		#ndb.delete_multi(qry.fetch(999999, keys_only=True))

		nursery_count2 = NurseryModel2.all().count()
		self.response.write( 'Nursery2 = %d<br/>'%(nursery_count2))

		nursery3_result = NurseryModel3.all(keys_only = True).fetch(999999)
		self.response.write( 'Nursery3 = %d<br/>'%(len(nursery3_result)))

		offset3 = getoffset3()
		self.response.write( 'Offset = %d<br/>'%(offset3))

	def test(self):
		pass

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/collect/(\w+)', CollectHandler),
    ('/data/(\w+)', DataHandler),
], debug=True)
