#!/usr/bin/env python

import pycurl
from cStringIO import StringIO as SIO

class SinglePut(object):
	"""SinglePut: Set a value for a record

	Requires initial input of the page to which a connection
	is to be established.  Provides the necessary methods to create and
	delete a JSESSION cookie
	:param page: base url for future actions
	"""
	def __init__(self,page):
		self.c = pycurl.Curl()
		self.setopt = self.c.setopt
		b = page[:-1] if page.endswith('/') else page
		self.basepage = b if b.endswith('REST') else b+'/REST'
		self.buf = SIO()
		self.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.logged = False
	def login(self,*creds):
		"""login function
		
		:param creds: arguements for username,password
			Note that these MUST be in this order.
		:return: 1 if login was successful 0 otherwise
		"""
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = '{base}/JSESSION'.format(base=self.basepage)
		self.setopt(pycurl.URL,uri)
		self.setopt(pycurl.USERPWD,'{0}:{1}'.format(*creds))
		self.c.perform()
		self.c.unsetopt(pycurl.USERPWD)
		self.cookie = self.buf.getvalue()

		if len(self.cookie)==32:
			self.logged = True
			return 1
		else:
			return 0
	def putfromuri(self,uri):
		"""Execute a put command based on input uri

		:param uri: query uri to submit to XNAT host
		:return: response from server
		"""
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = self.basepage+uri if uri.startswith('/') else self.basepage+'/'+uri
		self.setopt(pycurl.URL, uri)
		self.setopt(pycurl.COOKIE, 'JSESSIONID=%s'%self.cookie)
		self.setopt(pycurl.CUSTOMREQUEST, 'PUT');
		self.c.perform()
		self.buf.truncate()
		return self.buf.getvalue()
	def logout(self):
		"""disconnect from XNAT host
		
		:return: server response
		"""
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = '{base}/JSESSION'.format(base=self.basepage)
		self.setopt(pycurl.URL, uri)
		body = ''
		self.setopt(pycurl.COOKIE, "JSESSIONID=%s"%self.cookie)
		self.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
		self.c.perform()
		self.buf.truncate()
		body = self.buf.getvalue()
		self.c.close()
		self.logged = False
		self.buf.close()
		return body

