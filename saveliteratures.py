#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Turing Wong'
__date__='2018-7-22'
__desc__='Save the content to database!'

import getliteratures
import orm

def saveLiteratures():
    literature_id = 0
    while True:
        #获取页面内容
        soup = getliteratures.Requester.getHtml()
        print("总共%d页" %getliteratures.Requester.page_all)
        #解析页面内容，获得诗文
        literatures = getliteratures.Analysiser.getLiterature(soup)
        for literature in literatures:
            current_literature = orm.Base_literatures(literature_id=literature_id, literature_name=literature.title,literature_author=literature.author,literature_content=literature.content,literature_likes=literature.good,literature_tag=literature.tag,literature_type=literature.type_)
            current_literature.save()
            literature_id +=1
        if getliteratures.Requester.page_num > getliteratures.Requester.page_all:
            print("All page done!")
            break;
            
saveLiteratures()
