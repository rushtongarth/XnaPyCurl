#! /usr/bin/env python

import json,pycurl
from single import SingleQuery
from multi import MultiQuery
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

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
	def logout(self):
		"""logout method
		
		uses the method from SingleQuery class"""
		done = self.cxn.logout()
		return done

	def loadmulti(self,template,subsess,tail):
		"""load a multiquery pool
		
		creates a MultiQuery object from instance
		template: uri to format for multiquery
		subsess: subject session dict, keys are subjects; values are sessions
		tail: columns to output from query
		returns a list of pulled results"""
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





















