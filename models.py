# -*- coding:utf-8 -*-

import cgi
import os
import re
import json
from geo.geomodel import GeoModel, geotypes

from google.appengine.ext import ndb, db

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
