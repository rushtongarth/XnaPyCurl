#! /usr/bin/env python

import json,pycurl
from collections import OrderedDict as OD
from cStringIO import StringIO as StringIO
from single import SingleQuery
from multi import MultiQuery

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
#login
#logout
#getsubjects -single
#getexperiments -single
#getassessors -multi
#getscans -multi


class xnaPyCurl(object):
	"""xnaPyCurl: Connect and pull resources from XNAT
	
	Class requires an input url to the XNAT API from which 
	resources are to be pulled"""
	def __init__(self,basepage):
		self.basepage = basepage
		self.ci = PKCS1_OAEP.new(RSA.generate(2048))

	def login(self,*creds):
		"""login method
		
		requires user credentials as input as username,password pair
		gets a session cookie for future actions"""
		self.cxn = SingleQuery(self.basepage)
		ccount = self.cxn.login(*creds)
		self.crds = map(self.ci.encrypt,creds)
		return ccount

	def loadmulti(self,template,subsess,tail):
		mq = MultiQuery(self.basepage)
		ccount = mq.login(*map(self.ci.decrypt,self.crds))
		urilist = [template.format(subj=k,exp=v)+tail for k,v in subsess.iteritems() if v]
		mq = mq(urilist)
		raw = mq.getfromuri()
		mq.logout()
		return raw

	def getsubjects(self,project,uri_tail):
		uri = 'projects/{proj}/subjects?{tail}'.format(proj=project,tail=uri_tail)
		raw = self.cxn.getfromuri(uri)
		return [json.loads(raw)]
	def getexperiments(self,project,uri_tail):
		uri = 'projects/{proj}/experiments?{tail}'.format(proj=project,tail=uri_tail)
		raw = self.cxn.getfromuri(uri)
		return [json.loads(raw)]
	def getassessors(self,project,subjexpdict,uri_tail):
		uri = 'projects/{proj}'.format(proj=project)
		uri += '/subjects/{subj}/experiments/{exp}/assessors?'

		raw = self.loadmulti(uri,subjexpdict,'format=json')
		return map(json.loads,raw)
	def getscans(self,project,subjexpdict,uri_tail):
		uri = 'projects/{proj}'.format(proj=project)
		uri += '/subjects/{subj}/experiments/{exp}/scans?'
		raw = self.loadmulti(uri,subjexpdict,'format=json')
		return map(json.loads,raw)





















