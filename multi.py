#! /usr/bin/env python
#Nota bene:
# This class is an adaptation of an example provided in the pyCurl examples
# it can be found 
# here: https://github.com/pycurl/pycurl/blob/master/examples/retriever-multi.py

import json,pycurl,operator as op
from collections import OrderedDict as OD
from cStringIO import StringIO as SIO


class MultiGrab(object):
	def __init__(self,pageroot,pagelist=[]):
		b = page[:-1] if pageroot.endswith('/') else pageroot
		self.page = b if 'REST' in b and b.endswith('REST') else b+'/REST'
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

	def jardestroyer(self):
		c = pycurl.Curl()
		buf = SIO()
		uri = uri = '{base}/JSESSION'.format(base=self.page)
		c.setopt(pycurl.URL, uri)
		body = ''
		for cookie in self.cj:
			print "closing cxn: %s"%cookie
			c.setopt(pycurl.COOKIE, "JSESSIONID=%s"%cookie)
			c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
			c.setopt(pycurl.WRITEDATA, buf)
			c.perform()
			buf.truncate()
			body+=buf.getvalue()
			buf.reset()
		return body
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
	def login(self,*creds):
		if self.jarbuilder(*creds)==self.nc:
			# this should be logged
			self.allocater()
			numcxn = len(self.cj)
		else:
			self.allocator()
			numcxn = len(self.cj)
		return numcxn
	def logout(self):
		return self.jardestroyer()

	def __call__(self,pages):
		mg = MultiGrab(self.page,pagelist=pages)
		return mg


	def grab(self):
		## taken from 
		out = []
		freelist = self.h[:]
		num_proc = 0
		pn = 0
		while num_proc < self.numpage:
			# If there is a url to process and a free curl object
			# then, add to multi stack
			while self.pl and freelist:
				url = self.pl.pop(0)
				c = freelist.pop()
				buf = SIO()
				c.setopt(pycurl.URL, url)
				c.setopt(pycurl.WRITEFUNCTION, buf.write)
				self.m.add_handle(c)
				c.buf = buf
				c.url = url
				c.bname = 'page_%d'%pn
				pn+=1
			# Run the curl state machine for the multi stack
			while 1:
				ret, num_handles = self.m.perform()
				if ret != pycurl.E_CALL_MULTI_PERFORM:
					break
			# Add terminated curl objects to the freelist
			while 1:
				num_q, ok_list, err_list = self.m.info_read()
				for c in ok_list:
					out.append(c.buf.getvalue())
					c.buf.close()
					c.buf = None
					self.m.remove_handle(c)
					print("Success:", c.bname, c.url, c.getinfo(pycurl.EFFECTIVE_URL))
					freelist.append(c)
				for c, errno, errmsg in err_list:
					c.buf.close()
					c.buf = None
					m.remove_handle(c)
					print("Failed: ", c.bname, c.url, errno, errmsg)
					freelist.append(c)
				num_proc = num_proc + len(ok_list) + len(err_list)
				if num_q == 0:
					break
			# sleep until some more data is available.
			self.m.select(1.0)
		for c in self.h:
			if c.buf is not None:
				c.buf.close()
				c.buf = None
			c.close()
		self.m.close()
		return out
