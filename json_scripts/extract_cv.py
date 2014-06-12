#!/usr/bin/env python
#!-*- coding:utf8 -*-
#!vim: set ts=4 sw=4 sts=4 tw=100 noet:
# ***************************************************************************
# 
# Copyright (c) 2013 Baidu.com, Inc. All Rights Reserved
# $Id$ 
# 
# **************************************************************************/
 
 
 
import os
import sys
import json
import re
 
__date__ = '2013/11/30 20:50:34'
__revision = '$Revision$'

reremove = re.compile(r"[ \t]+")

def add_to_dict(dic,key,value):
	if not key in dic:
		dic[key] = str(value)
	else:
		dic[key] += ";"+str(value)

buf=""
for i in open(sys.argv[1]):
	i = i.strip()
	i = i.replace(r"\r","")
	i = i.replace(r"\n","")
	buf += i

items = json.loads(buf)
fname = sys.argv[1]

if "TargetJob" in items:
	TargetJob = items["TargetJob"]
	if "CurrentJobTitle_CN" in TargetJob and TargetJob["CurrentJobTitle_CN"]:
		jdtitle = reremove.sub("",TargetJob["CurrentJobTitle_CN"].lower().encode("utf8"))
		if len(jdtitle) > 0:
			sys.stdout.write("%s\t0\t%s\t1\n"%(fname, jdtitle ))
	if "KeyWords_CN" in TargetJob and TargetJob["KeyWords_CN"]:
		s = reremove.sub("",TargetJob["KeyWords_CN"].lower().encode("utf8") )
		if len(s) > 0:
			sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))
else:
	sys.stderr.write("Cannot find TargetJob,failed.\n")

if "SelfAssessment" in items and items["SelfAssessment"] and "CareerObjective_CN" in items["SelfAssessment"]:
	if items["SelfAssessment"]["CareerObjective_CN"]:
		s = reremove.sub("",items["SelfAssessment"]["CareerObjective_CN"].lower().encode("utf8"))
		if len(s) > 0:
			sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))

if "SkillAndStrength" in items and items["SkillAndStrength"]:
	if "OtherSkill_CN" in items["SkillAndStrength"] and items["SkillAndStrength"]["OtherSkill_CN"]:
		s = reremove.sub("",  items["SkillAndStrength"]["OtherSkill_CN"].lower().encode("utf8") )
		if len(s) > 0:
			sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))

if "WorkExperience" in items and "Work" in items["WorkExperience"]:
	Experience = items["WorkExperience"]
	Work = Experience["Work"]
	if Work:
		for workitem in Work:
			if "Job" not in workitem:
				continue

			Jobs = workitem['Job']
			for job in Jobs:
				if job["JobTitle_CN"]:
					s = reremove.sub("",job["JobTitle_CN"].lower().encode("utf8") )
					if len(s) > 0:
						sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))
				if job["JobDescription_CN"]:
					s = reremove.sub("",job["JobDescription_CN"].lower().encode("utf8"))
					if len(s) > 0:
						sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))



