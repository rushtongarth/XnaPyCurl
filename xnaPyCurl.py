#! /usr/bin/env python

import json,pycurl

from cStringIO import StringIO as StringIO

class xnaPyCurl(object):
	def __init__(self,basepage):
		self.basepage = basepage
