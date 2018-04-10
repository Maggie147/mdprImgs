#!/usr/bin/python python
# -*- coding: utf-8 -*-
"""
__title__ = 'python_2.7 [requests] get image v1.0'
__author__ = 'xxxx'
__ctime__ = '2017-10-31'
__mtime__ = '2018-04-10'

"""

import os
import sys
import pprint
import requests
import time
from requests import Request, Session
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup
# sys.path.append("../Common/pylib")
reload(sys)
sys.setdefaultencoding('utf8')


photo_folder = './img2/'

def usage(processName):
	print "Usage: %s URL  Path" % processName
	print "For example:"
	print "		..."


def get_nowtime(tStamp=1):
    '''tStamp is 1, return now time by timeStamp.'''
    if tStamp == 1:
        timeStamp = time.time()
        return timeStamp
    else:
        time_local  = time.localtime()
        YMD = time.strftime("%Y-%m-%d", time_local)
        return YMD

def GetMsgEx(url, para=None, cookies=None, data=None, filename=None, debug=0):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
		'Connection': 'keep-alive'}
	if para:
		for key in para.keys():
			if para[key] is None:
				del para[key]
			else:
				if key == 'User-Agent' and para['User-Agent'] != '':
					headers['User-Agent'] = para['User-Agent']
				else:
					headers[key] = para[key]
	if cookies and len(cookies) != 0:
		headers['cookie'] = cookies

	try:
		if not data or len(data) == 0:
			response = requests.get(url, headers=headers)
		else:
			response = response.post(url, headers=headers, data=data)
	except Exception as e:
		raise e
		return None
	if str(response.status_code)[0] != '2':
		print "HTTP error, status_code is %s,  url=%s"%(response.status_code, url)
		return None

	if debug:
		print url
		print response.status_code
		pprint.pprint(headers)

	if filename:
		with open(filename, 'wb') as fd:
			for response_data in response.iter_content(1024):
				fd.write(response_data)
		return filename
	else:
		return response.text


def get_img(argv):
	img_url = argv[0]
	debug   = argv[1]

	response = GetMsgEx(img_url.strip())
	if not response:
		print "request img_url[%s] error!" % img_url
		return None

	try:
		soup = BeautifulSoup(response, 'html.parser')
		main_photo = soup.find('figure', {"class":"main-photo f9em"})
		img_src = main_photo.find('img')['src'].strip()
	except Exception as e:
		print "BeautifulSoup analyse img_src error!"
		return None

	''' get img name'''
	img_name_tmp = img_src.split('/')[-1]
	img_name = img_name_tmp.split('?')[0]
	img_path = photo_folder.strip() + img_name.strip()

	filename = GetMsgEx(img_src, filename=img_path)
	if not filename:
		print "get img_src[%s] failed!"%img_src
		return None
	if debug:
		print "img_url: ", img_url
		print "img_src: ", img_src
	return filename


def get_imgUrls(first_url, debug):
	if not first_url:
		print "NO url to request!"
		return None

	headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate, br',
		'Upgrade-Insecure-Requests': '1',
		'Cache-Control': 'max-age=0'}

	response = GetMsgEx(first_url, headers)
	if not response:
		print "request first_url[%s] error!" % first_url
		return None

	try:
		soup = BeautifulSoup(response, 'html.parser')
		content_photo = soup.find('div', {'class': 'content-photo clearfix'})
	except Exception as e:
		print e
		return None

	img_urls = []
	img_urls = ['http://mdpr.jp' + figure.a['href'].strip() for figure in content_photo.findAll('figure', {"class":"square"})]
	if debug:
		print img_urls
	return img_urls


def start_fun(para, debug=0):
	time_start = get_nowtime()
	try:
		first_url = para['URL'].strip()
		img_path  = para['Path'].strip()
	except Exception as e:
		print e
		sys.exit()

	''' get img urls'''
	print "start get imgUrls..."
	img_urls = get_imgUrls(first_url, debug)
	if not img_urls or not isinstance(img_urls, list):
		print "get img_urls failed!!!"
		sys.exit()
	print "total img_url: ", len(img_urls)

	''' get img_src'''
	print "start get img_src, and download..."
	debugs = [debug]*len(img_urls)
	pool = Pool(6)
	filenames = pool.map(get_img, zip(img_urls, debugs))
	pool.close()
	pool.join()

	time_end = get_nowtime()
	print "Lasted %d seconds" % (time_end-time_start)


def main():
	para = {}
	argc = len(sys.argv)
	if argc == 1:
		para['URL']  = "http://mdpr.jp/photo/detail/4810818"
		para['Path'] = photo_folder
	elif argc == 3:
		para['URL'] = sys.argv[1]
		para['Path'] = sys.argv[2]
	else:
		usage(sys.argv[0])
		sys.exit(-1)

	''' make sure pic path is ok'''
	if not os.path.exists(para['Path']):
		os.makedirs(para['Path'])

	if not para['URL'] or not para['Path']:
		sys.exit()

	debug = 0
	start_fun(para, debug)


if __name__ == "__main__":
	main()
