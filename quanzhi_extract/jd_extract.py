#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2014-6-10
@summary: 职位信息关键词提取
@author: user
'''
import pymongo, re
from mongo_access import MongoAccess
from sqlalchemy import Table, Column, Integer, BLOB, String, MetaData, TEXT, DATETIME
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy import select, func, text

class Extractor(MongoAccess):
    def __init__(self):
#        super(MongoAccess, self).__init__()
        MongoAccess.__init__(self)
        self.g_conf = {
                        'type':'mysql',
                        'uname':'webuser',
                        'passwd':'test',
                        'database':'qz_tuijian_test',
                        'socket':'192.168.1.230:3306'
                       }
        self.query = {}
        self.cursor = None
        
    def get_con_string_by_conf(self):
        import os
        db_type = self.g_conf['type']
        if db_type == 'sqlite':
            return 'sqlite:///%s' % os.path.abspath(self.g_conf['socket'])
        elif db_type == 'mysql':
            return 'mysql://%s:%s@%s/%s?charset=utf-8' % (self.g_conf['uname'], self.g_conf['passwd'], self.g_conf['socket'], self.g_conf['database'])
        elif db_type == 'postgres':
            return 'postgresql://%s:%s@%s/%s' % (self.g_conf['uname'], self.g_conf['passwd'], self.g_conf['socket'], self.g_conf['database'])
        
        return None
    
    def get_engine(self, ctx = None, echo = True):
        from sqlalchemy import create_engine
        if ctx and hasattr(ctx, '_engine'):
            return getattr(ctx, '_engine')
        db_conn_string = self.get_con_string_by_conf()
        engine = create_engine(db_conn_string, echo = echo, convert_unicode = True)
        if ctx:
            setattr(ctx, '_engine', engine)
        return engine
    
    def _next_range(self):
        try:
            ipos = self.data_range_it.next()
            cursor = self.DB.C_Job.find(self.query, skip = ipos, limit = 1000)
            self.cursor = cursor
        except Exception, e:
            print e
            self.GetQuanzhiDb()
            
    def extract_jd(self, ctx):
        reremove = re.compile(r"[ \t]+")
        removebracket = re.compile(r"<.+?>")
        removeSentence = re.compile(r"[;:]+")
    
        """
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
        """
        jd_items = []
        try:
            ctx = ctx.strip()
            #ctx = ctx.replace(r'\n','')
            #ctx = ctx.replace(r'\r','')
            ctx = reremove.sub(" ",ctx)
            ctx = ctx.replace("<br >", "<br>")
    
            items = ctx
            #print items
            jd_items.append( (0, items['JobTitle'].encode("utf8").lower(), 1) )
            #sys.stdout.write("%s\t0\t%s\t1\n"%('aaa', items['JobTitle'].encode("utf8").lower()))
            jds = items['JobDescribe'].encode("utf8").lower().split("<br")
            for j in jds:
                j = removebracket.sub("",j)
                j = removeSentence.sub(" ", j)
                if len(j) < 10:
                    continue
                jd_items.append( (1, j.strip(), 1) )
                #sys.stdout.write("%s\t1\t%s\t1\n"%('aaa',j.strip()))
        except Exception as ex:
            print ex
            return []
        
        return jd_items

    def before_extract(self):
        self.GetQuanzhiDb()
        cursor = self.DB.C_Job.find(self.query)
        total_count = cursor.count()
        self.data_range_it = range(0, total_count, 1000).__iter__()
    
if __name__ == '__main__':
    ext = Extractor()
    ext.extract()