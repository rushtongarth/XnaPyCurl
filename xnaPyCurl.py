#! /usr/bin/env python

import json,pycurl
from cStringIO import StringIO as StringIO

class xnaPyCurl(object):
	def __init__(self,basepage):
		self.c = pycurl.Curl()
		self.setopt = self.c.setopt
		self.basepage = basepage
		self.buf = StringIO()
	def __getattr__(self,mode):
		if mode=='expr' or mode=='asr':
			return '{base}/experiments?{payload}'
		elif mode=='subj':
			return '{base}/subjects?{payload}'
		elif mode=='ses':
			return '{base}/JSESSION'
	def login(self,*creds):
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = self.ses.format(base=self.basepage)
		self.setopt(pycurl.URL,uri)
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.setopt(pycurl.USERPWD,'{user}:{pasw}'.format(user=creds[0],pasw=creds[1]))
		self.c.perform()
		self.buf.truncate()
		self.cookie = self.buf.getvalue()
		self.c.reset()
		return 1
	def logout(self):
		if self.buf.tell()!=0:
			self.buf.reset()
		uri = self.ses.format(base=self.basepage)
		self.setopt(pycurl.URL,uri)
		self.setopt(pycurl.COOKIE, "JSESSIONID=%s"%self.cookie)
		self.setopt(pycurl.CUSTOMREQUEST, "DELETE")
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.c.perform()
		self.c.close()
		self.buf.truncate()
		body = self.buf.getvalue()
		self.buf.close()
		return body
	def experiments(self,projlist,xsiList,columnDict):
		if self.buf.tell()!=0:
			self.buf.reset()
		for k,v in columnDict.items():
			if len(v):
				cols.append(','.join('%s/%s'%(k,i) for i in v))
			else:
				cols.append(k)
		payload={
			'xsiType':','.join(xsiList),
			'columns':','.join(cols),
			'format':'json',
			'project':','.join(projlist)
			}
		joined = '&'.join('%s=%s'%(k,v) for k,v in payload.items())
		uri = self.exp.format(base=self.basepage,payload=joined)
		self.setopt(pycurl.URL, uri)
		self.setopt(pycurl.COOKIE, "JSESSIONID=%s"%self.cookie)
		self.setopt(pycurl.WRITEDATA, self.buf)
		self.c.perform()
		self.buf.truncate()
		return json.loads(self.buf.getvalue())
	
