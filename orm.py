#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Turing Wong'
__date__='2018-7-8'
__desc__='Implementation the interface of exchanging data with database!'


import pymysql
import getliteratures


class Field(object):

    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)
    
    
class StringField(Field):

    def __init__(self, name):
        super(StringField, self).__init__(name, 'varchar(500)')

class IntegerField(Field):

    def __init__(self, name):
        super(IntegerField, self).__init__(name, 'bigint')
        

class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name=='Model':
            #print("super class:%s" %bases)
            return type.__new__(cls, name, bases, attrs)
        #print('Found model: %s' % name)
        mappings = dict()
        for k, v in attrs.items():
            if isinstance(v, Field):
                #print('Found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = name # 假设表名和类名一致
        return type.__new__(cls, name, bases, attrs)
    
class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
        
    def execute(self,sql):
        try:
            db = pymysql.connect("localhost","root","173904839","sudongpo" ,charset='utf8')
            #print('Successful connect!')
            crud = db.cursor()
            #print(self.values())
            crud.execute(sql,tuple(self.values()))
            #crud.execute("insert into Base_literatures (literature_id,literature_name,literature_content,literature_tag,literature_likes) values(%s,%s,%s,%s,%s)",(1, '题西林壁', '横看成岭侧成峰', '哲理', 20))
            if sql.find("select")!=-1:
                return_data = crud.fetchall()
            else:
                return_data=None
            db.commit()
            return return_data
        except ConnectionError as e:
            print(e.__cause__)
        finally:
            if db:
                db.close()
    
    def save(self):
        """
        添加内容
        """
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append('%s')
            args.append(getattr(self, k, None))
        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
        #print('SQL: %s' % sql)
        #print('ARGS: %s' % str(args))
        self.execute(sql)
        
        
    def find(self):
        """
        查找内容
        """
        args = ''
        for k in self:
            args += str(k)+"="+"%s"+" and "
        args+='1'
        sql = 'select * from %s where %s' % (self.__table__, args)
        #print('SQL: %s' % sql)
        #print('ARGS: %s' % str(args))
        return self.execute(sql)
        
    def delete(self):
        """
        删除内容
        """
        args = ''
        for k in self:
            args += str(k)+"="+"%s"+" and "
        args+='1'
        sql = 'delete from %s where %s' % (self.__table__, args)
        #print('SQL: %s' % sql)
        #print('ARGS: %s' % str(args))
        self.execute(sql)
        
class Base_literatures(Model):
    # 定义类的属性到列的映射：
    literature_id = IntegerField('literature_id')
    literature_name = StringField('literature_name')
    literature_author = StringField('literature_author')
    literature_content = StringField('literature_content')
    literature_likes = IntegerField('literature_likes')
    literature_tag = StringField('literature_tag')
    literature_type = StringField('literature_type')

if __name__=='__main__':
    soup = getliteratures.Requester.getHtml()
    literatures = getliteratures.Analysiser.getLiterature(soup)
    literature = literatures[0]
    literature = Base_literatures(literature_id=0, literature_name='苏东坡传',literature_author='林语堂',literature_content='真棒',literature_likes=1234,literature_tag='hao zhenhao',literature_type='传记')    
    if not literature.find():
        literature.save()
    else:
        print("苏东坡最牛逼！by %s" %__author__)
    
