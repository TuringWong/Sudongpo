#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Turing Wong'
__date__='2018-7-19'
__desc__='Implementation the interface of Request and Analysis!'

import re
import time
import os
import random
from zhon.hanzi import punctuation
import requests
from bs4 import BeautifulSoup

class Literature():
    def __init__(self,author,title,content,good,tag,type_):
        self.author = author
        self.title = title
        self.content = content
        self.good = good
        self.tag = tag
        self.type_ = type_
        
class Writer(object):
    def __init__(self,name,age,literature_sets=[]):
        self.name = name
        self.age = age
        self.literature_sets = literature_sets
        
    def addLiterature(self,literature):
        self.literature_sets.append(literature)
        
    def getLiteratures(self):
        return self.literature_sets
    
class Requester():
    page_num = 1
    page_all = 1
    
    @classmethod
    def getHtml(cls):
        url = "https://so.gushiwen.org/authors/authorvsw_3b99a16ff2ddA"+ str(Requester.page_num) +".aspx"
        headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'                
                }
        
        proxies_list = ['125.118.75.168:6666','171.13.37.221:23727','61.135.217.7:80','111.155.116.215:8123']
        proxies = {
                "http": "http://%s" %random.choice(proxies_list),
                }

        connect_times = 1
        while True:
            try:
                print("获取第%d页内容中..." % Requester.page_num)
                html = requests.get(url,headers=headers,proxies=proxies,timeout=5)
                #print(html.headers['user-agent'])
                break;
            except ConnectionError as e:
                print(str(e.errno),':Failed connection！',e.__cause__)
                print('\n')
                if connect_times >= 3:
                    print("Failed to connect 3 times，please check you network！")
                    os._exit()
                else:
                    print('Try to reconnect 5s later...')
                    connect_times += 1
                    time.sleep(5)
        Requester.soup = BeautifulSoup(html.text,'lxml')
        if Requester.page_num == 1:
            page_all = Requester.soup.body.select('.main3')[0].h1.span.string.strip()
            match_page = re.search('/.+页',Requester.soup.body.select('.main3')[0].h1.span.string.strip())
            Requester.page_all = int(page_all[match_page.start()+1:match_page.end()-1].strip())
        Requester.page_num += 1
        print("获取成功！")
        return Requester.soup
    
    @classmethod
    def reset(cls):
        cls.page_num = 1
        print("已重置从第1页开始获取！")
    
class Analysiser():
    ori_author = ''
    ori_title = ''
    content = ''
    ori_good = ''
    ori_tag = ''
    
    @classmethod
    def __analysisAuthor(cls,son_soup):
        au_dynas = son_soup.select('.source')[0].stripped_strings
        au_dyna=''
        for i in au_dynas:
            au_dyna += i
        cls.ori_author = au_dyna
        return str(au_dyna)
    
    @classmethod
    def __analysisTitle(cls,son_soup):
        for title in son_soup.select('.source')[0].previous_sibling.previous_sibling:
            title =  title.string.strip()
        cls.ori_title = title
        return str(title)
    
    @classmethod
    def __analysisContent(cls,son_soup):
        content = ''
        for contson in  son_soup.select('div[class="contson"]')[0].stripped_strings:
            content += contson
            
        #去除正文中注释的内容(即小括号内包裹的内容)
        compiler = re.compile(r'[(（].*?[)）]')
        content = compiler.subn('',content)[0]
        cls.content = content
        return str(content)
    
    @classmethod
    def __analysisGood(cls,son_soup):
        good = son_soup.select('div[class="good"]')[0].span.string.strip()
        cls.ori_good = good
        return int(good.strip())
    
    @classmethod
    def __analysisTag(cls,son_soup):
        tag=''
        try:
            for t in son_soup.select('.tag')[0].stripped_strings:
                tag += t
        except IndexError as e:
            tag = ''
        cls.ori_tag = tag
        #剔出原始tag中无意义的内容
        if tag:
            tag_list = str(tag).strip().split(sep='，')
            filter_tags = list(filter(lambda x: not re.search(r'[诗词文赋]',x.strip()),tag_list))
            tag = ' '.join(filter_tags)
        return str(tag)
    
    @classmethod
    def __analysisType_(cls,son_soup):
        #第1步：判断Tag中是否有“诗”、“词”,"赋"关键字
        if re.search(r'[诗词赋]',cls.ori_tag):
            type_ = re.search(r'[诗词赋]',cls.ori_tag).group()
        #第2步：判断Title中是否有“诗”、“词”,"赋"关键字
        elif re.search(r'[诗词赋]',cls.ori_title):
            type_ = re.search(r'[诗词赋]',cls.ori_title).group()
        #第3步：判断Title中是否有“.”
        elif cls.ori_title.find('·')!=-1:
            type_ = '词'
        #第4步：抽取三段，比较字符长度是否完全相同
        else:
            content_list = re.split(r'['+punctuation+r']',cls.content)
            content_choices = random.choices(content_list[:-1],k=3)
            if (len(content_choices[0])==len(content_choices[1])) and (len(content_choices[0])==len(content_choices[2])):
                type_ = '诗'
            else:
                type_='文'
        return str(type_)
    
    @classmethod
    def getLiterature(cls,soup):
        literatures=list()
        for son_soup in soup.find_all('div',class_="sons"):
            author = cls.__analysisAuthor(son_soup)
            title = cls.__analysisTitle(son_soup)
            content = cls.__analysisContent(son_soup)
            good = cls.__analysisGood(son_soup)
            tag = cls.__analysisTag(son_soup)
            type_ = cls.__analysisType_(son_soup)
            literature = Literature(author,title,content,good,tag,type_)
            literatures.append(literature)
        return literatures

if __name__=='__main__':
    soup  = Requester.getHtml()
    if soup:
        literatures = Analysiser.getLiterature(soup)
        for literature in literatures:
            print(literature.author)
            print(literature.title)
            print(literature.content)
            print(literature.good)
            print(literature.tag)
            print(literature.type_)
            print('\n')
        