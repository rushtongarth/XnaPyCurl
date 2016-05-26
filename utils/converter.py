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
	
def buildscript(flist,ofile=None):
	funks=[]
	for f in flist:
		func,opts = fileparse(f)
		funks.append(functionbuilder(func,opts))
	funcstr = '\n'.join(funks)
	pycurlcode=Main_Template.format(functions=funcstr)
	if ofile:
		with open(ofile,'w') as out:
			out.write(pycurlcode)
		return pycurlcode
	return pycurlcode

parser = argparse.ArgumentParser(description='Convert libcurl to pycurl.')
parser.add_argument('-f','--file',type=str, nargs='?',help='Input file to convert to pycurl code')
parser.add_argument('-o','--output',type=str,nargs='?',help='File where output should be written')
parser.add_argument('-v','--verbose',action='store_true',help='Print the conversion to standard out even if writing to file')
if __name__ == '__main__':
	args = parser.parse_args()
	if args.file:
		fls = [args.file]
		if args.output:
			script = buildscript(fls,args.output)
		else:
			script = buildscript(fls)
		if args.verbose or not args.output:
			print script
		
	else:
		sys.exit(1)
