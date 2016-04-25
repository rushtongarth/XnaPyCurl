#! /usr/bin/env python

import json,pycurl,operator as op
from collections import OrderedDict as OD
from cStringIO import StringIO as SIO



class CurlQuery(object):
	def __init__(self,page):
		self.c = pycurl.Curl()
		self.setopt = self.c.setopt
		b = page[:-1] if page.endswith('/') else page
		self.basepage = b if b.endswith('REST') else b+'/REST'
		self.buf = SIO()
		self.logged = False
	def getfromuri(self,uri):
		if self.buf.tell()!=0:
			self.buf.reset()
		self.setopt(pycurl.URL, uri)
		self.setopt(pycurl.COOKIE, 'JSESSIONID=%s'%self.cookie)
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.c.perform()
		self.buf.truncate()
		return json.loads(self.buf.getvalue())

	def login(self,*creds,**kwargs):
		if not self.logged:
			self.c = pycurl.Curl()
			self.setopt = self.c.setopt
			self.buf = SIO()
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = '{base}/JSESSION'.format(base=self.basepage)
		self.setopt(pycurl.URL,uri)
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.setopt(pycurl.USERPWD,'{0}:{1}'.format(*creds))
		self.c.perform()
		self.cookie = self.buf.getvalue()
		self.c.reset()
		if len(self.cookie)==32:
			self.logged = True
			return 1
		else:
			return 0

	def logout(self):
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = '{base}/JSESSION'.format(base=self.basepage)
		self.setopt(pycurl.URL, uri)
		body = ''
		self.setopt(pycurl.COOKIE, "JSESSIONID=%s"%self.cookie)
		self.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.c.perform()
		self.buf.truncate()
		body = self.buf.getvalue()
		self.c.close()
		self.logged = False
		self.buf.close()
		return body

		
	
