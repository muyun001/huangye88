# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 13:43:58 2019

@author: wd-fxt
"""
import re
import math
import requests
import codecs
from lxml import etree
from lxml.html import fromstring
import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123456',
                             db='spider_data',
                             charset='utf8mb4')


def insert(com_id, com_name, products, com_addr, people, telephone, com_introduce):
    print((com_id, com_name, products, com_addr, people, telephone, com_introduce))
    with connection.cursor() as c:  # 修改数据--查询、删除、修改
        c.execute("insert into com_info_3(uid, com_name, products, com_addr, people, telephone, com_introduce) values('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(com_id, com_name.strip(), products.strip(), com_addr.strip(), people.strip(), telephone.strip(), com_introduce.strip()))
    connection.commit()


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'Hm_lvt_c8184fd80a083199b0e82cc431ab6740=1548727173; Hm_lpvt_c8184fd80a083199b0e82cc431ab6740=1548727653',
    'Host': 'b2b.huangye88.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}


def get_city_hrefs():
    '''
    获取各省的链接
    '''
    all_city_url_list = []
    start_url = 'http://b2b.huangye88.com/qiye/wangzhan/'
    city_url_xpath = '/html/body/div[3]/div[3]/div[2]/div[2]/div[2]/a/@href'
    try:
        response = requests.get(start_url).text
        province_href = etree.HTML(response).xpath('/html/body/div[3]/div[3]/div[2]/div[1]/div[2]//a/@href')
        # 测试每个省的数据量是否大于50页，如果大于50页，就分城市查询
        for href in province_href:
            page_num = get_com_num(href)
            if page_num > 50:
                city_url_list = etree.HTML(response).xpath(city_url_xpath)
                for url in city_url_list:
                    page_num = get_com_num(url)
                    if page_num > 50:
                        response = requests.get(url, headers=headers).text
                        sec_cityurl_list = etree.HTML(response).xpath(city_url_xpath)
                        for i in sec_cityurl_list:
                            all_city_url_list.append(i)
                    else:
                        all_city_url_list.append(url)
            else:
                all_city_url_list.append(href)
        return all_city_url_list
    except Exception, e:
        print('get province hrefs error', e.args)


def get_com_num(province_url):
    '''获取数量'''
    page_num_xpath = '/html/body/div[3]/div[3]/div[1]/div[3]/div[1]/span/em/text()|/html/body/div[3]/div[3]/div[1]/div[2]/div[1]/span/em/text()'
    response = requests.get(province_url, headers=headers).text
    com_num = etree.HTML(response).xpath(page_num_xpath)
    page_num = int(math.ceil(int(int(com_num[0]) + 19) / 20.0))  # 根据公司个数，每页显示20个，求得有多少页
    return page_num


def get_all_com_url(href):
    '''
    获取每个省的所有公司的url
    '''
    parse_xpath = '/html/body/div[3]/div[3]/div[1]/div[3]//dt//h4/a/@href|/html/body/div[3]/div[3]/div[1]/div[2]/div[2]//dt//h4/a/@href'
    page_num_xpath = '/html/body/div[3]/div[3]/div[1]/div[3]/div[1]/span/em/text()|/html/body/div[3]/div[3]/div[1]/div[2]/div[1]/span/em/text()'

    try:
        response = requests.get(href, headers=headers).text
        com_num = etree.HTML(response).xpath(page_num_xpath)  # 求出公司的个数
        page_num = int(math.ceil(int(int(com_num[0]) + 19) / 20.0))  # 根据公司个数，每页显示20个，求得有多少页
        if page_num > 50:  # 超过50页的都不现实，所以若超过50页就赋值为50
            page_num = 50

        com_url = []  # 每个省份的所有公司的url
        # 按页循环，解析出每页所有公司的url
        for page in range(1, page_num + 1):
            print(page)
            response = requests.get(href + 'pn%s' % page, headers=headers).text
            com_url_list = etree.HTML(response).xpath(parse_xpath)  # 解析出公司的url
            for url in com_url_list:
                com_url.append(url)
        return com_url
    except Exception, e:
        print('get all company`s urls error', e.args)


# def parse(url):
#     '''
#     解析页面，获得公司名称/公司地址/主营产品/联系人/联系电话/公司介绍。
#     '''
#     com_name_xpath = '/html/body/div[4]/div[2]/div[1]/div[2]/div/p/text()|/html/body/div[3]/div[2]/div[1]/div[2]/div/p/text()|/html/body/div[5]/div[1]/div[1]/div[3]/p[1]/text()'  # 公司名称的xpath
#     products_xpath = '/html/body/div[4]/div[2]/div[1]/div[2]/div/ul/li[4]/a/text()|/html/body/div[4]/div[2]/div[1]/div[2]/div/ul/li[7]/text()|/html/body/div[4]/div[2]/div[1]/div[2]/div/ul/li[6]/text()|/html/body/div[3]/div[2]/div[1]/div[2]/div/ul/li[8]/text()|/html/body/div[5]/div[2]/div/div[4]/table/tbody/tr[1]/td[2]/text()'  # 主营产品的xpath
#     com_addr_xpath = '/html/body/div[4]/div[1]/div[1]/div[2]/ul[2]/li[3]/text()|/html/body/div[4]/div[1]/div[1]/div[2]/ul[2]/li[3]/a/text()|/html/body/div[3]/div[1]/div[1]/div[2]/ul[2]/li[3]/a/text()|/html/body/div[3]/div[1]/div[1]/div[2]/ul[2]/li[3]/text()|/html/body/div[5]/div[2]/div/div[4]/table/tbody/tr[3]/td[1]/text()'  # 公司地址的xpath
#     people_xpath = '/html/body/div[4]/div[1]/div[2]/div[2]/ul/li[1]/a/text()|/html/body/div[3]/div[1]/div[2]/div[2]/ul/li[1]/a/text()|/html/body/div[5]/div[1]/div[1]/div[3]/p[2]/text()'  # 联系人的xpath
#     telephone_xpath = '/html/body/div[1]/div/div[2]/div/text()|/html/body/div[5]/div[1]/div[1]/div[3]/p[3]/text()'  # 联系电话的xpath
#     com_introduce_xpath = '/html/body/div[4]/div[2]/div[2]/div[2]/p[1]/text()|/html/body/div[3]/div[2]/div[2]/div[2]/p[1]/text()|/html/body/div[5]/div[2]/div/div[2]/p/text()'  # 公司介绍的xpath
#
#     # 当域名不以‘http://b2b.huangye88.com/’开始时，headers的host会改变
#     if not url.startswith('http://b2b.huangye88.com/'):
#         headers['Host'] = re.findall('http://(.*?)/',url)[0]
#     else:
#         headers['Host'] = 'b2b.huangye88.com'
#     url = url+'company_detail.html'
#
#     try:
#         response = requests.get(url, headers=headers).text
#
#         com_name = ''.join(etree.HTML(response).xpath(com_name_xpath))
#         products = ''.join(etree.HTML(response).xpath(products_xpath))
#         com_addr = ''.join(etree.HTML(response).xpath(com_addr_xpath))
#         people = ''.join(etree.HTML(response).xpath(people_xpath))
#         telephone = ''.join(etree.HTML(response).xpath(telephone_xpath))
#         com_introduce = ''.join(etree.HTML(response).xpath(com_introduce_xpath))
#
#         insert(url, com_name, products, com_addr, people, telephone, com_introduce)
#
#         com_info = '%s|%s|%s|%s|%s|%s' % (com_name, people, telephone, products, com_addr, com_introduce)
#         return com_info
#     except Exception, e:
#         print('xpath parse error', e.args, 'url:%s' % url)
#         return ''


def get_all_urls():
    '''
    调用方法，获取所有公司的url
    '''
    all_city_url_list = get_city_hrefs()  # 获取各个城市的链接

    all_com_urls_list = []  # 所有省份所有公司的url的集合
    for href in all_city_url_list:
        com_url = get_all_com_url(href)
        if com_url == None:
            continue
        for url in com_url:
            all_com_urls_list.append(url)

    return all_com_urls_list

# def get_com_id(url):
#     '''获取网页id'''
#     try:
#         if url.startswith('http://b2b.huangye88.com/qiye'):
#             com_id = re.findall('http://b2b.huangye88.com/qiye(\d*?)/', url)[0]
#         elif url.startswith('http://b2b.huangye88.com/gongsi'):
#             com_id = re.findall('http://b2b.huangye88.com/gongsi/(\d*?)/', url)[0]
#         else:
#             response = requests.get(url, headers=headers).text
#             com_id = re.findall(r'<input type="hidden" name="info\[uid\]" value="(\d*?)">', response, re.S)[0]
#         return com_id
#     except Exception, e:
#         print('get com_id error', e.args)


def get_headers(url):
    '''设置headers中“Host”的内容'''
    if url.startswith('http://b2b.huangye88.com/qiye') or url.startswith('http://b2b.huangye88.com/gongsi'):
        headers['Host'] = 'b2b.huangye88.com'
    else:
        headers['Host'] = re.findall('http://(.*?)/',url)[0]
    return headers


def extract_html(url, parse_failed_url):
    '''网页解析'''

    headers = get_headers(url)
    # com_id = get_com_id(url)
    url = url + 'company_detail.html'
    response = requests.get(url, headers=headers).text
    html_obj = etree.HTML(response)
    try:
        com_name = html_obj.cssselect("h1.big")[0]  # 公司名
        com_name = com_name.text
        com_introduce = etree.tostring(html_obj.cssselect('div.r-content p.txt')[0])  # 公司简介
        items = html_obj.cssselect('ul.con-txt > li')
        for item in items:
            label = item.find('label')
            # print(label.text)
            if label.text == u'主营产品：':
                products = label.tail
            if label.text == u"所在地：":
                com_addr = label.tail
        tel_items = html_obj.cssselect('div.c-left > div:nth-child(2) > div.l-content >ul >li')
        for item in tel_items:
            label = item.find('label')
            if label.text == u'联系人：':
                people = item.find('a').text
            if label.text == u'手机：':
                telephone = label.tail
        if 'telephone' not in dir():
            telephone = ''
        # if 'telephone' not in dir():
        #     telephone = ''
    except Exception, e:
        print('exextract html arror', e.args)
        parse_failed_url.append(url)
        pass
    try:
        print(com_name.encode('utf-8'))
        insert(url, com_name.encode('utf-8'), str(products.encode('utf-8')), str(com_addr.encode('utf-8')), str(people.encode('utf-8')), str(telephone.encode('utf-8')), str(com_introduce.encode('utf-8')))
    except Exception, e:
        print('insert to mysql error', e.args)


def run():
    # global urls, parse_failed_url
    # urls = get_all_urls()  # 获取所有公司url
    # # with codecs.open('all_urls.txt','w') as w:

    parse_failed_url = []  # 将解析失败的url放入此list

    with codecs.open('huangye88_all_urls.txt','r') as f:
        urls = f.readlines()
        for url in urls:
            # if not url.startswith('http://b2b.huangye88.com/qiye'):
            print(url)
            extract_html(url.strip(), parse_failed_url)
    # with codecs.open('com_info.txt','w','utf-8') as w:
    #     for url in urls:
    #         print(url)
    #         com_info = extract_html(url)
    #         if com_info != '':  # 如果返回的结果是‘’，则为解析出问题，放入此list
    #             w.write(com_info + '\n')
    #         else:
    #             parse_failed_url.append(url)


if __name__ == '__main__':
    # from multiprocessing.dummy import Pool
    # pool = Pool(processes=4)
    run()
    # extract_html(url='http://gzfq1452.b2b.huangye88.com/')





