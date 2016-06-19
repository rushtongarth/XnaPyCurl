#!/usr/bin/env python

import operator as op
import urllib2 as ul
import itertools as it
import xml.etree.ElementTree as ET
ns = {'schema': 'http://www.w3.org/2001/XMLSchema'}

class parser(object):
	def __init__(self,page):
		f = ul.urlopen(page)
		self.root = ET.fromstring(f.read())
		f.close()
	def gettypes(self):
		self.ct = self.root.findall('schema:complexType',ns)
		return self.ct
	def basetypes(self):
		self.ct = self.root.findall('schema:complexType',ns)
		extns = lambda x: x.findall('.//*schema:extension',ns)
		elmts = lambda X: set(reduce(lambda y,z: y+z,map(lambda x: x.findall('.//*schema:element',ns),X[::2])))
		L = [(k,i) for i in self.ct for k in extns(i) if k.get('base','').startswith('xnat')]
		L = sorted(L,key=lambda x: x[0].get('base',''))
		grouped = it.groupby(L,key=lambda x: x[0].get('base',''))
		D = {t[1].get('name',''):(t[1],k,t[0]) for k,g in grouped for t in g}
		bases = {}
		for k in D.keys():
			vals = map(lambda x: x.get('name',''),elmts(D[k]))
			if vals:
				bases[k] = vals
			else:
				tmp = D[k][1].replace('xnat:','')
				if not D.has_key(tmp):
					continue
				bases[k] = map(lambda x: x.get('name',''),elmts(D[D[k][1].replace('xnat:','')]))
		return bases



if __name__=='__main__':
	basepage='https://central.xnat.org/schemas/xnat/xnat.xsd'
	P = parser(basepage)
	test = P.basetypes()
	for k,v in test.items():
		print k,v
