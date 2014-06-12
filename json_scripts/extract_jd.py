#!/usr/bin/env python
#!-*- coding:utf8 -*-
#!vim: set ts=4 sw=4 sts=4 tw=100 noet:
# ***************************************************************************
# 
# 
# **************************************************************************/
 
 
 
import os
import sys
import json 
import re
 
__date__ = '2013/11/25 19:42:41'
__revision = '$Revision$'

reremove = re.compile(r"[ \t]+")
removebracket = re.compile(r"<.+?>")

for i in open(sys.argv[1]):
	i = i.strip()
	i = i.replace(r'\n','')
	i = i.replace(r'\r','')
	i = reremove.sub(" ",i)
	i = i.replace("<br >", "<br>")
	try:
		items = json.loads(i)
		sys.stdout.write("%s\t0\t%s\t1\n"%(sys.argv[1], items['JobTitle'].encode("utf8").lower()))
		jds = items['JobDescribe'].encode("utf8").lower().split("<br")
		for j in jds:
			j = removebracket.sub("",j)
			if len(j) < 10:
				continue
			sys.stdout.write("%s\t1\t%s\t1\n"%(sys.argv[1],j.strip()))
	except:
		break



