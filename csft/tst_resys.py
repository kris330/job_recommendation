# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    测试推荐与检索的集成方案。
    1 输入记录编号 或 key， 得到 Resume 的关键词；
        '1', '4f82b8546ec463d7e403a3e2', 
    2 使用关键词在 Sphinx 中进行近似检索
      - 按字段进行排序
    3 使用扩展，重新进行排序
"""
import sys
import os
import zlib
import re
import json
from sphinxapi import *

pwd = os.path.abspath(os.getcwd())
# ./build/lib.linux-x86_64-2.7/
mmseg_so_path = os.path.join(pwd, '..', 'build', 'lib.linux-x86_64-2.7')
#print mmseg_so_path
sys.path.insert(0, mmseg_so_path)


from sqlalchemy import Table, Column, Integer, BLOB,  String, MetaData, TEXT, DATETIME
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy import select, func, text
from sqlalchemy.sql import and_, or_, not_

import binascii

def safe_crc32(s):
    return binascii.crc32(s) & 0xffffffff

def get_conn_string_by_conf(conf):
    """
        从配置信息中创建数据库的连接方式， 配置信息应该包括：
        type in {sqlite|mysql|postgres}   socket  uname   passwd  database
        Ref:
            http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
    """
    import os
    db_type = conf['type']
    if db_type == 'sqlite':
        # 'sqlite:////absolute/path/to/foo.db'
        return "sqlite:///%s" % os.path.abspath( conf['socket'] )  # we use abs path only.
    if db_type == 'mysql':
        # 'mysql://scott:tiger@localhost/foo'
        return "mysql://%s:%s@%s/%s?charset=utf8" % ( conf['uname'], conf['passwd'], conf['socket'] , conf['database'])
    if db_type == 'postgres':
        # postgresql://scott:tiger@localhost/mydatabase
        return "postgresql://%s:%s@%s/%s" % ( conf['uname'], conf['passwd'], conf['socket'] , conf['database'])
    return None


def get_engine(db_conn_string,ctx=None, echo=True):
    # ast as ctx's property.
    from sqlalchemy import create_engine
    if ctx and hasattr(ctx, '_engine'):
        return getattr(ctx, '_engine')
    engine = create_engine(db_conn_string, echo=echo, convert_unicode=True)
    if ctx:
        setattr(ctx, '_engine', engine)
    return engine


g_conf = {
    'type':'mysql',
    'uname':'nzinfo',
    'passwd':'123456',
    'database':'quanzhi',
    'socket':'192.168.2.1:3306'
}
g_conf = {
    'type':'mysql',
    'uname':'webuser',
    'passwd':'test',
    'database':'qz_tuijian_test',
    'socket':'192.168.1.230:3306'
}

g_sph_conf = {
    'host':'192.168.2.1',
    'port': 9312,
    'database': 'quanzhi'
}

g_sph_conf = {
    'host':'192.168.1.235',
    'port': 9312,
    'database': 'resys'
}

g_metadata = MetaData()
table_name = 'resumes'
#table_name = 'jobs'
#table_name_keys = 'jobs_keys'
table_name_keys = 'resumes_keys'

tbl_resume = Table(table_name, g_metadata,
                   Column('tid', BIGINT, primary_key=True),
                   Column('key', String(255), unique=True),     # 文件名，主键
                   Column('data', BLOB),                        # 配置项的值
                   )

tbl_keys = Table(table_name_keys, g_metadata,
                   Column('tid', BIGINT, primary_key=True),
                   Column('title_key', TEXT ),     # 文件名，主键
                   Column('info_key', TEXT),                        # 配置项的值
                   )

def create_tables(engine):
    """
        创建数据库
    """
    global g_metadata
    global tbl_resume
    g_metadata.create_all(engine)     # create the table
    return True

def get_weighted_keys(txt):
    # quick & dirty fix
    if type(txt) == unicode:
        txt = txt.encode('utf-8')
    keys = []
    txt = txt.replace(';:', ':')
    toks = txt.split(';')
    #print toks, txt
    for tok in toks:
        tok = tok.strip()
        if not tok:
            continue
        #print tok, tok.split(':')
        try:
            pairs = tok.split(':')
            if len(pairs) < 2:
                continue # ignore the parse error.
            key = pairs[0]
            weight = pairs[-1]
            weight = int(weight) + 1 
            #idx = int(weight) + baseidx
        except ValueError as ve:
            print txt, tok, tok.split(':')
            continue
            #exit(0)
        keys.append( (key, weight) )
    return keys

def get_query_keys(txt):
    keys = get_weighted_keys(txt)
    if len(keys):
        keys = [safe_crc32(x[0]) for x in keys]
    return keys

def get_calc_keys(txt):
    keys = get_weighted_keys(txt)
    if len(keys):
        keys = [(safe_crc32(x[0]), x[1]) for x in keys]
    #print keys
    keys= sorted (keys, key=lambda x: x[0], reverse=False)
    #print keys
    #exit(0)
    return keys

def sph_query(q):
    global g_sph_conf
    cl = SphinxClient()
    cl.SetServer ( g_sph_conf['host'], g_sph_conf['port'] )
    field_weights = []
    for i in range(0, 125): #[0, 124]
        field_weights.append(i+1)
    for i in range(125, 250): #[125, 249]
        field_weights.append(i - 125 + 1)
    cl.SetWeights ( field_weights )
    #?setweights()是什么用法?field_weights = [1,2,3,4...125,1,2,3,4...,125]检索的时候，coreseek不知道你各个字段的权重值，所以需要指定
    #各个字段的权重值，SetWeights()只需要传递一个权重值组成的列表，就能知道所有字段的权重值了
    #改：使用setfieldweights()方法，传递一个字段{'字段':'权重值'}，除了扩展字段，剩下不设置，默认为1
    cl.SetLimits ( 0, 1000 )
    cl.SetMatchMode ( SPH_MATCH_EXTENDED2 )
    # default limit 0, 1000
    res = cl.Query ( q, g_sph_conf['database'] )

    return res, cl

def get_result_docids(res, cl):
    rs = []
    if not res:
        return rs

    if res.has_key('matches'):
        for match in res['matches']:
            rs.append(match['id'])
    return rs

def dump_res(res, cl):
    if not res:
        print 'query failed: %s' % cl.GetLastError()
        sys.exit(1)

    if cl.GetLastWarning():
        print 'WARNING: %s\n' % cl.GetLastWarning()

    print 'Query retrieved %d of %d matches in %s sec' % (res['total'], res['total_found'], res['time'])
    print 'Query stats:'

    if res.has_key('words'):
        for info in res['words']:
            print '\t\'%s\' found %d times in %d documents' % (info['word'], info['hits'], info['docs'])

    if res.has_key('matches'):
        n = 1
        print '\nMatches:'
        for match in res['matches']:
            attrsdump = ''
            for attr in res['attrs']:
                attrname = attr[0]
                attrtype = attr[1]
                value = match['attrs'][attrname]
                if attrtype==SPH_ATTR_TIMESTAMP:
                    value = time.strftime ( '%Y-%m-%d %H:%M:%S', time.localtime(value) )
                attrsdump = '%s, %s=%s' % ( attrsdump, attrname, value )

            print '%d. doc_id=%s, weight=%d%s' % (n, match['id'], match['weight'], attrsdump)
            n += 1

def main(argv):
    global g_conf
    global tbl_resume
    global g_metadata

    Enable_KEYEA = True
    #?什么参数?
    if Enable_KEYEA:
        import _jobrmd  

    engine = get_engine(get_conn_string_by_conf(g_conf), echo = False)

    # load record
    rec_id = argv[1]
    stmt = None
    if len(rec_id) == len('4f82b8546ec463d7e403a3e2'):
        # find by key
        stmt = select([tbl_keys]).select_from(
                tbl_keys.join(tbl_resume, 
                    and_(
                    tbl_resume.c.tid==tbl_keys.c.tid,
                ))
                ).where(tbl_resume.c.key==rec_id)
    else:
        # find by id
        rec_id = int(rec_id)
        stmt = select([tbl_keys]).select_from(tbl_keys).where(tbl_keys.c.tid==rec_id)
    
    if stmt == None:
        exit(0)

    if Enable_KEYEA:
        job_ke = _jobrmd.Jobrmd()
        job_ke.load('./jobrmd.model')

    #print stmt
    #g_metadata.reflect(bind=engine)
    row = engine.execute( stmt ).fetchone()
    """
        1 create template table
        2 insert all search result
        3 do join query.
        4 get all rows
        5 pass to _jobrmd ext
        6 resort by score.
    """
    if row:
        #print row.title_key, row.info_key
        keys = get_query_keys(row.title_key)
        keys.extend( get_query_keys(row.info_key) )
        q = ' '.join([str(x) for x in keys])
        #?此处可以字符串/3是什么意思？：一堆词，命中3个就算命中了，3是经验值，其他值检索出来的结果都不大准确
        res, cl = sph_query('"%s"/%d' % (q, 3))
        #dump_res(res, cl)
        cv_title_key = row.title_key
        cv_info_key = row.info_key
        #cv?简历关键词
        cv = ( get_calc_keys(row.title_key) , get_calc_keys(row.info_key) )
        #print 'cv=', cv
        ids = get_result_docids(res, cl)
        if len(ids):
            import _jobrmd 

            connection = engine.connect()
            result = connection.execute("""
                CREATE TEMPORARY TABLE SphinxResult (
                    tid BIGINT NOT NULL primary key
                )
                """)
            ids = [{"id":x} for x in ids]
            #使用mysql的一张临时表，性能比较高（而不是直接根据id值去查另外一张表），先插入再联合查询出来（一个查询一个connection，每个查询都创建一张表），mysql只能想到这种方案，mongodb不知道
            connection.execute(text("""
                INSERT INTO SphinxResult(tid) VALUES (:id)
                """), ids)
            #print len(ids)
            rs = connection.execute("""
                SELECT SphinxResult.tid as tid, jobs.key as job_key, jobs_keys.title_key as title, jobs_keys.info_key as info
                 FROM SphinxResult LEFT JOIN jobs_keys ON SphinxResult.tid = jobs_keys.tid
                                   LEFT JOIN jobs ON jobs.tid = SphinxResult.tid
                """)  
            items = []
            for row in rs:
                #print row.tid, row.title, row.info
                jd = ( get_calc_keys(row.title) , get_calc_keys(row.info) )
                #?jd和cv，calc_score()该方法有何用?，jd是查询出来的职位描述，cv是简历，查询出来的关键词与原关键词比对，算出相似度，再做排序
                score = _jobrmd.calc_score(jd, cv)
                #print score, row.job_key
                #print 'jd=', jd, score
                items.append(
                    (score, row.job_key, row.title, row.info)
                    )
            items =  sorted (items, key=lambda x: x[0], reverse=True)
            print 'query=', cv_title_key, cv_info_key
            for i in range(0, len(items)):
                item = items[i]
                print "No%d."%i, item[0], item[1], item[2], item[3]
            connection.close()
        #print row.title_key
        pass
    # for


if __name__ == "__main__":
    #filelist = sys.argv[1]
    #data_path = sys.argv[2]
    main(sys.argv)

# -*- end of file -*-