# -*- coding:utf-8 -*-
# coreseek3.2 python source演示
# author: HonestQiao
# date: 2010-06-03 11:46
from sqlalchemy import Table, Column, Integer, BLOB,  String, MetaData, TEXT, DATETIME
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy import select, func
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
        return "mysql://%s:%s@%s/%s" % ( conf['uname'], conf['passwd'], conf['socket'] , conf['database'])
    if db_type == 'postgres':
        # postgresql://scott:tiger@localhost/mydatabase
        return "postgresql://%s:%s@%s/%s" % ( conf['uname'], conf['passwd'], conf['socket'] , conf['database'])
    return None

g_metadata = MetaData()
table_name_keys = 'jobs_keys'
tbl_keys = Table(table_name_keys, g_metadata,
                   Column('tid', BIGINT, primary_key=True),
                   Column('title_key', TEXT ),     # 文件名，主键
                   Column('info_key', TEXT),                        # 配置项的值
                   )

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
    'uname':'root',
    'passwd':'',
    'database':'quanzhi',
    'socket':'127.0.0.1:3306'
}


class MainSource(object):
    def __init__(self, conf):
        global g_conf
        self.conf =  conf
        self.idx = 0
        self.engine = get_engine(get_conn_string_by_conf(g_conf), echo = False)
        self.data = [] # if not init []; else None
        self.data_range_it = None
        

    def GetScheme(self):  #获取结构，docid、文本、整数
        fields = [
            ('id' , {'docid':True, } ),
            #('title_ft', { 'type':'text'} ),
            #('info_ft', { 'type':'text'} ),
            ('title', {'type':'string'} ),
            ('info', {'type':'string'} ),
        ]
        for i in range(0, 250):#
            #?添加250个全文字段，作用？,还得需要包含该索引的其他字段
            fields.append( ('ft_%d' % i, {'type':'text'} ) )
        return fields

    def GetFieldOrder(self): #字段的优先顺序，字段的顺序没有关系
        fields_order = []
        for i in range(0, 250):
            fields_order.append( 'ft_%d' % i ) 
        #print tuple(fields_order)
        return [tuple(fields_order), ]
        
    def Connected(self):   #如果是数据库，则在此处做数据库连接
        engine = self.engine
        self.total_count = engine.execute( select([func.count()]).select_from(tbl_keys) ).fetchone()[0]
        self.data_range_it = range(0, self.total_count, 1000).__iter__()
        #print total_count
        pass

    def NextDocument(self, err):   #取得每一个文档记录的调用
        def fill_data(txt, baseidx, maxidx):
            # quick & dirty fix
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
                    idx = int(weight) + baseidx
                except ValueError as ve:
                    print txt, tok, tok.split(':')
                    continue
                    #exit(0)

                if idx > maxidx:
                    #?权重都大于125，此时field_name不会被覆盖，self.__getattribute__(field_name)先获取，再设置
                    idx = maxidx
                field_name = 'ft_%d' % idx
                #由于coreseek目前不支持对某个字段设置权重值，所以只能根据算好的权重值来命名field字段，再根据字段名对应权值关系来设置检索字段的权重
                orig_txt = self.__getattribute__(field_name)
                orig_txt += ' ' + str(safe_crc32(key))
                #?为何全文字段的值都是crc32整数字符串?，防止被mmseg分词切碎，crc32有千分之几的重复率，可以使用md5（python拍脑门想就想到crc32函数）
                #查询也是等价的，用户不关心是怎么查的，因为系统会先算出来这个值，再去查
                #print orig_txt
                self.__setattr__(field_name, orig_txt)
        
        def dump_data():
            for i in range(0, 250):
                print i, self.__getattribute__('ft_%d' % i)

        if self.data == None:
            return False

        if self.data == [] or self.idx == len(self.data):
            # fetch next range
            if self._next_range():
                self.idx = 0

        # reset all fields.
        for i in range(0, 250):
            self.__setattr__('ft_%d' % i, '')

        if self.idx < len(self.data):
            item = self.data[self.idx]
            self.docid = self.id = item['id'] #'docid':True
            #print item['title_key']
            #print item['info_key']
            #self.title_ft = item['title_key'].encode('utf-8')
            #self.info_ft = item['info_key'].encode('utf-8')
            self.title = item['title_key'].encode('utf-8')
            self.info = item['info_key'].encode('utf-8')
            #?250二分?，作用？
            fill_data(self.title, 0, 124)
            fill_data(self.info, 125, 249)
            self.idx += 1
            #dump_data()
            #exit(0)
            return True
        else:
            return False

    def _next_range(self):
        try:
            ipos = self.data_range_it.next()
            s = tbl_keys.select(bind=self.engine).offset(ipos).limit(1000)
            rs = s.execute()
            self.data = []
            for row in rs:
                self.data.append({
                    'id': row.tid,
                    'title_key': row.title_key,
                    'info_key': row.info_key
                    })
            return True # ? the row count?
        except StopIteration:
            return False

if __name__ == "__main__":    #直接访问演示部分
    conf = {}
    source = MainSource(conf)
    source.Connected()

    while source.NextDocument():
        print "id=%d, subject=%s" % (source.docid, source.subject)
    pass
#eof
