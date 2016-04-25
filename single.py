#! /usr/bin/env python

import json,pycurl,operator as op
from collections import OrderedDict as OD
from cStringIO import StringIO as StringIO



class CurlQuery(object):
	def __init__(self,page):
		self.c = pycurl.Curl()
		self.setopt = self.c.setopt
		b = page[:-1] if page.endswith('/') else page
		self.basepage = b if b.endswith('REST') else b+'/REST'
		self.buf = StringIO()
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
		cxns = kwargs.get('cxncount',0)
		if not self.logged:
			self.c = pycurl.Curl()
			self.setopt = self.c.setopt
			self.buf = StringIO()
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = self.ses.format(base=self.basepage)
		self.setopt(pycurl.URL,uri)
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.setopt(pycurl.USERPWD,'{0}:{1}'.format(*creds))
		if cxns:
			jar = []
			for i in xrange(cxns):
				self.c.perform()
				tmpcookie = self.buf.getvalue()
				if len(tmpcookie)==32:
					jar.append(tmpcookie)
				self.buf.reset()
				self.buf.truncate()
			self.cookies = jar[:]
			self.logged = True
			return len(self.cookies)
		else: 
			self.c.perform()
			self.cookie = self.buf.getvalue()
			self.c.reset()
			if len(self.cookie)==32:
				self.logged = True
				return 1
		return 0
		
