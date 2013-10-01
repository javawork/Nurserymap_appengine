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
from datahandler import DataHandler
from collecthandler import CollectHandler
from models import *
from geo.geomodel import GeoModel, geotypes

from google.appengine.api import users
from google.appengine.ext import ndb, db
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import memcache

import webapp2

#class MainHandler(webapp2.RequestHandler):
#    def get(self):
#        self.redirect("/maptest")

app = webapp2.WSGIApplication([
    #('/', MainHandler),
    ('/collect/(\w+)', CollectHandler),
    ('/data/(\w+)', DataHandler),
], debug=True)
