#! /usr/bin/env python
#Nota bene:
# This class is an adaptation of an example provided in the pyCurl examples
# it can be found 
# here: https://github.com/pycurl/pycurl/blob/master/examples/retriever-multi.py

import pycurl
from cStringIO import StringIO as SIO


class MultiQuery(object):
	"""MultiQuery class
	
	Class for parallel queries to XNAT
	"""
	def __init__(self,pageroot,pagelist=[]):
		"""
		Initialize a MultiQuery Object
		
		:param pageroot: XNAT API url, NB: this will be prepended to all elements of pagelist
		
		:param pagelist: list of page uris of the form
		projects/<project_ID>...?<querystring>
		"""
		b = page[:-1] if pageroot.endswith('/') else pageroot
		self.page = b if 'REST' in b and b.endswith('REST') else b+'/REST'
		self.pl = pagelist
		self.numpage = len(pagelist)
		self.nc = 10
		self.m = pycurl.CurlMulti()
		self.h = []

	def jarbuilder(self,*creds):
		"""
		build a cookiejar of connections
		NB: This will create multiple connections to the server 
		
		:param creds: user login creditentials i.e. username,password
		:return: integer representing the number of connections that have been established
		"""
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
		"""
		disconnection helper function
		
		For all connections established in jarbuilder send the
		disconnect command to the server
		
		:returns: server response (empty string if successful)
		"""
		c = pycurl.Curl()
		buf = SIO()
		uri = uri = '{base}/JSESSION'.format(base=self.page)
		c.setopt(pycurl.URL, uri)
		body = ''
		for cookie in self.cj:
			print "closing cxn: %s"%cookie
			c.setopt(pycurl.COOKIE, "JSESSIONID=%s"%cookie)
			c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
			c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
			c.setopt(pycurl.WRITEDATA, buf)
			c.perform()
			buf.truncate()
			body+=buf.getvalue()
			buf.reset()
		for c in self.h:
			if c.buf is not None:
				c.buf.close()
				c.buf = None
			c.close()
		self.m.close()
		
		return body
	def allocater(self):
		"""
		Pre-allocate a list of curl objects
		"""
		for cookie in self.cj:
			c = pycurl.Curl()
			c.buf = None
			c.setopt(pycurl.FOLLOWLOCATION, 1)
			c.setopt(pycurl.MAXREDIRS, 5)
			c.setopt(pycurl.CONNECTTIMEOUT, 30)
			c.setopt(pycurl.TIMEOUT, 300)
			c.setopt(pycurl.NOSIGNAL, 1)
			c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
			c.setopt(pycurl.COOKIE,'JSESSIONID=%s'%cookie)
			self.h.append(c)
	def login(self,*creds):
		"""
		login to XNAT server
		
		:param creds: username,password
		:returns: number of established connections
		"""
		if self.jarbuilder(*creds)==self.nc:
			# this should be logged
			self.allocater()
			numcxn = len(self.cj)
		else:
			self.allocator()
			numcxn = len(self.cj)
		if numcxn>1:
			print 'Serial is for suckers...'
		return numcxn
	def logout(self):
		"""
		log out of all established connections
		"""
		return self.jardestroyer()

	def __call__(self,pages):
		"""
		populate the pagelist attribute if not previously done
		
		:param pages: a list of uris of the form
			projects/<project_ID>...?<querystring>
		
		:returns: a MultiQuery Object
		"""
		if hasattr(self,'cj'):
			self.pl = [self.page+i if i.startswith('/') else self.page+'/'+i for i in pages]
			self.numpage = len(pages)
			return self
		else:
			mg = MultiQuery(self.page,pages)
			return mg

	def getfromuri(self):
		"""
		Traverse the pagelist and make the appropriate query to the server
		
		.. note:: This strategy was adapted from the pycurl examples, specifically:
			`this example <https://github.com/pycurl/pycurl/blob/master/examples/retriever-multi.py>`_
		
		:returns: output from all queries
		"""
		out = []
		freelist = self.h[:]
		num_proc,pn = 0,0
		while num_proc < self.numpage:
			# If there is a url to process and a free curl object
			# then, add to multi stack
			while self.pl and freelist:
				url = self.pl.pop(0)
				c = freelist.pop()
				buf = SIO()
				c.setopt(pycurl.URL, url)
				c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
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
		return out
