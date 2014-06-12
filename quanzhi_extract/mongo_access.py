# coding=utf-8

'''
Created on 2011-11-29
@summary:
@author: chenhailong
'''

import pymongo, re, time
from pymongo import ReadPreference
from pymongo import ReplicaSetConnection

MongoDbAction_Find = 1
MongoDbAction_FindOne = 2
MongoDbAction_Remove = 3
MongoDbAction_Update = 4
MongoDbAction_Insert = 5

class MongoAccess( object ):
    '''
    @summary: 数据访问基类
    '''

    def __init__( self ):
        '''
        @summary: 构造方法
        '''

        self.DB = ''
        '''保存验证时间,超过一定时间，就验证一次'''
        self.authenticationTime = int( time.time() )
        self.mongoDbUser =  'dev'
        self.mongoDbPassword =  'test'
        self.mongoDbHost =  'mongo241,mongo242'
        self.replicaSetName =  'foo'
        
    def GetTestDb(self,connectAgain = False ,isSECONDARYONLY = False):
        '''
        @summary: 获取quanzhi数据库
        '''
        dbName = 'test'
        self.getConnection( dbName ,isSECONDARYONLY )
    
    def GetQuanzhiDb( self , connectAgain = False ,isSECONDARYONLY = False):
        '''
        @summary: 获取quanzhi数据库
        '''
        dbName = 'quanzhi'
        self.getConnection( dbName ,isSECONDARYONLY )

    def GetQuanzhiFileDb( self , connectAgain = False ,isSECONDARYONLY = False):
        '''
        @summary: 获取quanzhiFile数据库
        '''
        dbName = 'quanzhiFile'
        self.getConnection( dbName ,isSECONDARYONLY )

    def GetQuanzhiCvDb( self , connectAgain = False ,isSECONDARYONLY = False):
        '''
        @summary: 获取quanzhiCV数据库
        '''
        dbName = 'quanzhiCV'
        self.getConnection( dbName ,isSECONDARYONLY )

    def GetCrmDb( self, connectAgain = False ,isSECONDARYONLY = False):
        '''
        @summary: 获取Crm数据库
        '''
        dbName = 'crm'
        self.getConnection( dbName ,isSECONDARYONLY )
        
    def GetQuanzhiHunterDb(self, connectAgain = False, isSECONDARYONLY = False):
        '''
        @summary: 获取quanzhiHunter数据库
        '''
        dbName = 'quanzhiHunter'
        self.getConnection(dbName, isSECONDARYONLY)
        
    def GetQuanzhiBehaviorDb(self, connectAgain = False, isSECONDARYONLY = False):
        '''
        @summary: 获取quanzhiBehavior数据库
        '''
        dbName = 'quanzhiBehavior'
        self.getConnection(dbName, isSECONDARYONLY)
        
    def GetWeixinDb(self,connectAgain = False, isSECONDARYONLY = False):
        dbName = 'weixin'
        self.getConnection(dbName, isSECONDARYONLY)

    def getConnection( self, dbName ,isSECONDARYONLY = True):
        '''
        @summary: 获取连接
        @param dbName: 要连接的数据库
        '''
        tryMaxNum = 100
        tryNum = 0
        while tryNum < tryMaxNum:
            tryNum = tryNum + 1
            try:
                conn = ReplicaSetConnection( self.mongoDbHost, replicaSet = self.replicaSetName )
                self.DB = conn[dbName]
                if isSECONDARYONLY:
                    self.DB.read_preference = ReadPreference.PRIMARY
                else:
                    self.DB.read_preference = ReadPreference.PRIMARY
                self.DB.authenticate( self.mongoDbUser, self.mongoDbPassword)
                break
            except Exception, e:
                time.sleep(5)


    def GetObjectId( self, id = None ):
        '''
        @summary: 获取mongodb id
        @param id: id
        @return: ObjectId对象
        '''
        import pymongo
        if pymongo.version == '2.4.2':
            from bson.objectid import ObjectId
        else:
            from pymongo.objectid import ObjectId
            
        return ObjectId( id )

    @property
    def ASCENDING( self ):
        '''
        @summary: pymongo.ASCENDING
        '''
        return pymongo.ASCENDING

    @property
    def DESCENDING( self ):
        '''
        @summary: pymongo.DESCENDING
        '''
        return pymongo.DESCENDING

    def find(self,queryDict,collection,fields = None,Db = None):
        if not Db:
            Db = self.DB
        DbObj = getattr(Db ,collection)
        if fields:
            cursor = DbObj.find(queryDict,fields = fields)
        else:
            cursor = DbObj.find(queryDict)
        self.__log(collection,MongoDbAction_Find,Db)
        return cursor
    
    def find_one(self,queryDict,collection,fields = None,Db = None):
        if not Db:
            Db = self.DB
        DbObj = getattr(Db ,collection)
        if fields:
            result = DbObj.find_one(queryDict,fields = fields)
        else:
            result = DbObj.find_one(queryDict)
        self.__log(collection,MongoDbAction_FindOne,Db)
        return result
    
    def insert(self,insertDict,collection,wait = 1,Db = None):
        if not Db:
            Db = self.DB
        DbObj = getattr(Db ,collection)
        result = DbObj.insert(insertDict,w = wait)
        self.__log(collection,MongoDbAction_Insert,Db)
        return result
    
    def remove(self,queryDict,collection,Db = None):
        if not Db:
            Db = self.DB
        DbObj = getattr(Db ,collection)
        result = DbObj.remove(queryDict)
        self.__log(collection,MongoDbAction_Remove,Db)
        return result
    
    def update(self,queryDict,updateDict,collection,Db = None):
        if not Db:
            Db = self.DB
        DbObj = getattr(Db ,collection)
        result = DbObj.update(queryDict,updateDict)
        self.__log(collection,MongoDbAction_Update,Db)
        return result
    
    def __log(self,collectionName,Action,Db):
        '''
        @summary: 记录数据库的操作日志
        @param collectionName: 表名
        @param Action: 动作
        @param Db: 数据库对象
        '''
        msg = '''DbName:%s,CollectionName:%s,Action:%s''' % (Db.name,collectionName,Action)
        
    def __GetDBObject( self, entity ):
        '''
        @summary: 获取mongodb数据库集合对象
        @param entity: 实体对象
        @return: mongodb collection
        '''
        collectionName = type( entity ).__name__
        dbObj = eval( "self.DB." + collectionName )

        return dbObj

    def SetAttributeValue( self, entity, dict ):
        '''
        @summary: 填充对象属性值
        @param entity: 对象
        @param dict: 对象字典值
        '''
        import types
        for key in dict.keys():
            if entity.__dict__.has_key( key ):    #一对多数据填充
                if type( dict[key] ) == types.ListType:
                    childEntities = []
                    for childDict in dict[key]:
                        if type( childDict ) == types.ListType or type( childDict ) == types.DictionaryType:
                            childEntity = self.CreateModelClassInstance( key )
                            self.SetAttributeValue( childEntity, childDict )
                            childEntities.append( childEntity )
                        else:
                            childEntities.append( childDict )
                    entity.__setattr__( key, childEntities )
                elif type( dict[key] ) == types.DictionaryType:    #一对一数据填充
                    childEntity = self.CreateModelClassInstance( key )
                    self.SetAttributeValue( childEntity, dict[key] )
                    entity.__setattr__( key, childEntity )
                else:
                    if key == "_id":
                        entity.__setattr__( "_id", str( dict[key] ) )
                    else:
                        entity.__setattr__( key, dict[key] )

        return entity

    def CreateModelClassInstance( self, key ):
        '''
        @summary: 创建一个对象实例
        @return: entity
        '''
        pass

    def GetEntityParameters( self, entity, saveNone = False ):
        '''
        @summary: 获得对象的参数字典
        @param entity: 实体对象
        @param saveNone: 是否保存None值
        @return: dict
        '''
        import types
        parameters = {}
        try:
            dict = entity.__dict__
        except:
            #普通数据类型
            if type( entity ) == types.ListType:
                parameters = []
                for obj in entity:
                    parameters.append( self.GetEntityParameters( obj, saveNone ) )
                return parameters
            elif type( entity ) == types.TupleType:
                parameters = []
                for obj in entity:
                    parameters.append( self.GetEntityParameters( obj, saveNone ) )
                return parameters
            elif type( entity ) == types.DictType:
                dict = entity
            else:
                return entity

        for key in dict.keys():
            if key == "_id":
                if dict[key] <> None and dict[key] <> "" :
                    parameters[key] = self.GetObjectId( dict[key] )
            else:
                if dict[key] <> None:
                    parameters[key] = self.GetEntityParameters( dict[key], saveNone )
                else:
                    if saveNone:
                        parameters[key] = None
        else:
            pass

        return parameters

if __name__ == '__main__':
    obj = MongoAccess()
    obj.GetTestDb()
    a = obj.remove({'_id':obj.GetObjectId('52aabe6042a87e32c1661ff2')}, 'test')
