#! /usr/bin/env python

import os,re,sys,argparse
from cStringIO import StringIO as StringIO

buff = StringIO()
Main_Template="""
#!/usr/bin/env python
import pycurl
from cStringIO import StringIO as StringIO
{functions}
"""
functiontemplate="""
def {funcname}(*args,**kwargs):
	buffer = StringIO()
	c = pycurl.Curl()
	{curloptions}
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	c.close()
	body = buffer.getvalue()
	return body
"""
def fileparse(infile):
	t=os.path.basename(infile)
	func = os.path.splitext(t)[0]
	pat1 = 'curl_easy_setopt'
	pat2 = '.*CURLOPT_(?P<option>(URL|CUSTOMREQUEST|COOKIE).*);'
	with open(infile,'r') as f:
		x = f.read().split('\n')
	
	options = filter(lambda Y: pat1 in Y,x)
	s = re.compile(pat2)
	options = filter(s.match,options)
	bases = [s.match(i).group('option') for i in options]
	return func,bases

def functionbuilder(func,optlist):
	opts = '\n\t'.join(['c.setopt(c.%s'%base for base in optlist])
	return functiontemplate.format(funcname=func,curloptions=opts)
	
def buildscript(flist):
	funks=[]
	for f in flist:
		func,opts = fileparse(f)
		funks.append(functionbuilder(func,opts))
	funcstr = '\n'.join(funks)
	print Main_Template.format(functions=funcstr)

parser = argparse.ArgumentParser(description='Convert libcurl to pycurl.')
parser.add_argument('-f','--file',type=str, nargs='?',help='Input file to convert to pycurl code')
if __name__ == '__main__':
	args = parser.parse_args()
	if args.file:
		#func,opts = fileparse(args.file)
		buildscript([args.file])
	else:
		sys.exit(1)
