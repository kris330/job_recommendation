# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import os
import json

pwd = os.path.abspath(os.getcwd())
# ./build/lib.linux-x86_64-2.7/
mmseg_so_path = os.path.join(pwd, 'build', 'lib.linux-x86_64-2.7')
#print mmseg_so_path
sys.path.insert(0, mmseg_so_path)
mmseg_so_path = os.path.join(pwd, 'build', 'lib.linux-x86_64-2.6')
sys.path.insert(0, mmseg_so_path)

import _jobrmd

"""
  get_keyword():
  return title_key, info_key  

test_jd/5178ae0ca45512cdb0a03997.json	0	中心校长/中心主任（急）	1
test_jd/5178ae0ca45512cdb0a03997.json	1	工作职责：	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>1、 负责营运团队的建设和管理,制定销售策略和计划；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>2、 带领销售团队提供完整的客户服务以实现团队预算销售收入；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>3、 负责营运部各岗位的流程管理，协调各部门各岗位关系以保证学校营运顺畅；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>4、 定期培训、监督部门员工的销售操作行为；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>5、 协调市场部和教务部门完成销售的相应工作;	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>6、 完成部门签约并确保收款及时性、准确性；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>7、 确保信息系统内容及时准确性。	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>任职资格：	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>1、 大专以上学历，市场营销专业或受过营销类培训为佳；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>2、 5年以上销售工作经验，其中2年以上管理经验；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>3、 良好的职业形象、管理能力、沟通能力、领导能力；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>4、 熟练使用办公软件、办公自动化设备。	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>5、 工作认真、热情、主动性强；	1
test_jd/5178ae0ca45512cdb0a03997.json	1	>6、 有相关行业背景者优先。	1

"""

if True:
   job_ke = _jobrmd.Jobrmd()
   #print dir(job_ke)
   print job_ke.load('./jobrmd.model')
   infos = [
   		(0, u"中心校长/中心主任（急）", 1),
   		(1, u"工作职责：", 1),
   		(1, u">1、 负责营运团队的建设和管理,制定销售策略和计划；", 1),
   		(1, u">2、 带领销售团队提供完整的客户服务以实现团队预算销售收入；", 1),
   		(1, u">3、 负责营运部各岗位的流程管理，协调各部门各岗位关系以保证学校营运顺畅；", 1),
   		(1, u">4、 定期培训、监督部门员工的销售操作行为；", 1),
   		(1, u">5、 协调市场部和教务部门完成销售的相应工作;", 1),
   		(1, u">6、 完成部门签约并确保收款及时性、准确性；", 1),
   		(1, u">7、 确保信息系统内容及时准确性。", 1),
   		(1, u">任职资格：", 1),
   		(1, u">1、 大专以上学历，市场营销专业或受过营销类培训为佳；", 1),
   		(1, u">2、 5年以上销售工作经验，其中2年以上管理经验；", 1),
   		(1, u">3、 良好的职业形象、管理能力、沟通能力、领导能力；", 1),
   		(1, u">4、 熟练使用办公软件、办公自动化设备。", 1),
   		(1, u">5、 工作认真、热情、主动性强；", 1),
   		(1, u">6、 有相关行业背景者优先。", 1),

   ]
   keys = job_ke.keywords(infos)
   title_key, info_key = keys
   print json.dumps(title_key)
   for item in title_key:
   	 key, weight = item
   	 print key, weight
   	 
   for item in info_key:
   	 key, weight = item
   	 print key, weight

#5178ae0ca45512cdb0a03997
