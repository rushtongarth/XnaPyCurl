import json,pycurl,operator as op
from collections import OrderedDict as OD
from cStringIO import StringIO as SIO


class MultiGrab(object):
	def __init__(self,pageroot,pagelist=[]):
		b = page[:-1] if page.endswith('/') else page
		self.page = b if 'REST' in b and b.endswith('REST') else b+'/REST'
		self.page = pageroot
		self.pl = pagelist
		self.numpage = len(pagelist)
		self.nc = 5
		self.m = pycurl.CurlMulti()
		self.h = []

	def jarbuilder(self,*creds):
		
		c = pycurl.Curl()
		buf = SIO()
		uri = '{base}/JSESSION'.format(base=self.page)
		c.setopt(pycurl.URL,uri)
		c.setopt(pycurl.WRITEDATA, buf)
		c.setopt(pycurl.USERPWD,'{0}:{1}'.format(*creds))
		self.cj = []
		for i in xrange(self.nc):
			c.perform()
			tmpcookie = buf.getvalue()
			if len(tmpcookie)==32:
				self.cj.append(tmpcookie)
			buf.reset()
			buf.truncate()
		return len(self.cj)
	def allocater(self):
		# Pre-allocate a list of curl objects
		for cookie in self.cj:
			c = pycurl.Curl()
			c.buf = None
			c.setopt(pycurl.FOLLOWLOCATION, 1)
			c.setopt(pycurl.MAXREDIRS, 5)
			c.setopt(pycurl.CONNECTTIMEOUT, 30)
			c.setopt(pycurl.TIMEOUT, 300)
			c.setopt(pycurl.NOSIGNAL, 1)
			c.setopt(pycurl.COOKIE,'JSESSIONID=%s'%cookie)
			self.h.append(c)
