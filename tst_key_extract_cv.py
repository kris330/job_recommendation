# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    从 MySQL 中读取数据，进行关键词提取 ； 并保存
"""
import sys
import os
import zlib
import re
import json

pwd = os.path.abspath(os.getcwd())
# ./build/lib.linux-x86_64-2.7/
mmseg_so_path = os.path.join(pwd, 'build', 'lib.linux-x86_64-2.7')
#print mmseg_so_path
sys.path.insert(0, mmseg_so_path)
mmseg_so_path = os.path.join(pwd, 'build', 'lib.linux-x86_64-2.6')
sys.path.insert(0, mmseg_so_path)


from sqlalchemy import Table, Column, Integer, BLOB,  String, MetaData, TEXT, DATETIME
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy import select, func, text

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


g_metadata = MetaData()
table_name = 'resumes'
#table_name = 'jobs'
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


def proc_data(engine, files, data_path):
    global tbl_resume
    items = []
    for f in files:
        f = f.strip()
        fname = os.path.join(data_path, f)
        if os.path.isfile(fname):
            with open(fname,'r') as fh:
                ctx = fh.read()
        else:
            sys.stderr.write('file not found. %s' % fname)
            sys.stderr.flush()

        ctx_compress = zlib.compress(ctx, 9)
        #print len(ctx), len(ctx_compress)
        item = {'key': f[:-5], 'data': ctx_compress}
        items.append(item)
    engine.execute( tbl_resume.insert().values(items) )
    pass

def extract_jd(ctx):
    reremove = re.compile(r"[ \t]+")
    removebracket = re.compile(r"<.+?>")

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

        items = json.loads(ctx)
        #print items
        jd_items.append( (0, items['JobTitle'].encode("utf8").lower(), 1) )
        #sys.stdout.write("%s\t0\t%s\t1\n"%('aaa', items['JobTitle'].encode("utf8").lower()))
        jds = items['JobDescribe'].encode("utf8").lower().split("<br")
        for j in jds:
            j = removebracket.sub("",j)
            if len(j) < 10:
                continue
            jd_items.append( (1, j.strip(), 1) )
            #sys.stdout.write("%s\t1\t%s\t1\n"%('aaa',j.strip()))
    except Exception as ex:
        print ex
        return []
    return jd_items

def extract_cv(ctx):
    buf=""
    for i in ctx.splitlines(True):
        i = i.strip()
        i = i.replace(r"\r","")
        i = i.replace(r"\n","")
        buf += i
    
    reremove = re.compile(r"[ \t]+")

    items = json.loads(buf)
    #fname = sys.argv[1]
    jd_items = []

    if "TargetJob" in items and items["TargetJob"]:
        TargetJob = items["TargetJob"]
        if "CurrentJobTitle_CN" in TargetJob and TargetJob["CurrentJobTitle_CN"]:
            jdtitle = reremove.sub("",TargetJob["CurrentJobTitle_CN"].lower().encode("utf8"))
            if len(jdtitle) > 0:
                jd_items.append( (0, jdtitle.lower(), 1) )
                #sys.stdout.write("%s\t0\t%s\t1\n"%(fname, jdtitle ))
        if "KeyWords_CN" in TargetJob and TargetJob["KeyWords_CN"]:
            s = reremove.sub("",TargetJob["KeyWords_CN"].lower().encode("utf8") )
            if len(s) > 0:
                jd_items.append( (1, s.strip(), 1) )
                #sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))
    else:
        sys.stderr.write("Cannot find TargetJob,failed.\n")
        return []

    if "SelfAssessment" in items and items["SelfAssessment"] and "CareerObjective_CN" in items["SelfAssessment"]:
        if items["SelfAssessment"]["CareerObjective_CN"]:
            s = reremove.sub("",items["SelfAssessment"]["CareerObjective_CN"].lower().encode("utf8"))
            if len(s) > 0:
                jd_items.append( (1, s.strip(), 1) )
                #sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))

    if "SkillAndStrength" in items and items["SkillAndStrength"]:
        if "OtherSkill_CN" in items["SkillAndStrength"] and items["SkillAndStrength"]["OtherSkill_CN"]:
            s = reremove.sub("",  items["SkillAndStrength"]["OtherSkill_CN"].lower().encode("utf8") )
            if len(s) > 0:
                jd_items.append( (1, s.strip(), 1) )
                #sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))

    if "WorkExperience" in items and items["WorkExperience"] and "Work" in items["WorkExperience"]:
        Experience = items["WorkExperience"]
        Work = Experience["Work"]
        if Work:
            for workitem in Work:
                if "Job" not in workitem:
                    continue

                Jobs = workitem['Job']
                if not Jobs:
                    continue
                for job in Jobs:
                    if job["JobTitle_CN"]:
                        s = reremove.sub("",job["JobTitle_CN"].lower().encode("utf8") )
                        if len(s) > 0:
                            jd_items.append( (1, s.strip(), 1) )
                            #sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))
                    if job["JobDescription_CN"]:
                        s = reremove.sub("",job["JobDescription_CN"].lower().encode("utf8"))
                        if len(s) > 0:
                            jd_items.append( (1, s.strip(), 1) )
                            #sys.stdout.write("%s\t1\t%s\t1\n"%(fname, s))

    return jd_items

def main():
    global g_conf
    global tbl_resume
    global g_metadata

    Enable_KEYEA = True
    if Enable_KEYEA:
        import _jobrmd  

    engine = get_engine(get_conn_string_by_conf(g_conf), echo = False)

    #tbl_resume.drop(engine, checkfirst=True)
    #create_tables(engine)
    tbl_keys.create(engine, checkfirst=True)

    if Enable_KEYEA:
        job_ke = _jobrmd.Jobrmd()
        job_ke.load('./jobrmd.model')

    #g_metadata.reflect(bind=engine)
    total_count = engine.execute( select([func.count()]).select_from(tbl_resume) ).fetchone()[0]
    def key_info2string(keys):
        s = ''
        for item in keys:
            key, weight = item
            s += "%s:%d;" % (key, weight)
        #print s, type(s)
        return s.decode('utf-8')

    for i in range(393000, total_count, 1000):
        s = tbl_resume.select(bind=engine).offset(i).limit(1000)
        rs = s.execute()
        items = []
        for row in rs:
            #print row.key
            ctx = zlib.decompress(row.data)
            #print ctx
            try:
                jd_items = extract_cv(ctx)
            except ValueError as err:
                items.append(
                    {
                        'tid': row.tid,
                        'title_key': '',
                        'info_key': ''
                    }
                )
                continue

            #for item in jd_items:
            #    print item
            if Enable_KEYEA:
                keys = job_ke.keywords(jd_items)
                items.append(
                    {
                        'tid': row.tid, 
                        'title_key': key_info2string(keys[0]), 
                        'info_key': key_info2string(keys[1])
                    }
                )
                #s1 = key_info2string(keys[0])
                #print s1, type(s1)
        #break
        if len(items):
            engine.execute(text("INSERT INTO resumes_keys (tid, title_key, info_key) VALUES (:tid, :title_key, :info_key)").execution_options(autocommit=True), items )

    """
    tbl_resume
    with open(filelist, 'r') as fh:
        lines = fh.readlines()
    for i in range(0, len(lines), 200):
        end_pos = min(len(lines), i+200)
        proc_data(engine, lines[i:end_pos], data_path)
        print i,
        sys.stdout.flush()
    """
    # for


if __name__ == "__main__":
    #filelist = sys.argv[1]
    #data_path = sys.argv[2]
    main()

# -*- end of file -*-
