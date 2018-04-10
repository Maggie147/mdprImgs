# -*- coding: utf-8 -*-
"""
__title__ = '[requests] get image v2.0'
__author__ = 'xxxx'
__ctime__ = '2018-04-10'
"""
import os
import sys
import pprint
import requests
import time
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup
# reload(sys)
# sys.setdefaultencoding('utf8')

class DealWithArgv(object):
    def __init__(self, debug):
        self.debug = debug
        self.enter_url = "http://mdpr.jp/photo/detail/4810818"
        self.save_path = ''
        self.__argvCheck()

    def __argvCheck(self):
        if len(sys.argv) == 1:
            path = input("save_dir Name: ")
        elif len(sys.argv) == 3:
            self.enter_url = sys.argv[1].strip()
            path = sys.argv[2].strip()
        else:
            self.__usage(sys.argv[0])
            sys.exit(-1)
        self.save_path = self.__isValidPath(path)

    def __isValidPath(self, buf):
        try:
            buff = buf.strip()
            tmpdir = buff if buff else time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            mydir = './' + str(tmpdir) + '/'
            if not os.path.exists(mydir):
                os.makedirs(mydir)
            return mydir
        except Exception as e:
            print(e)
            sys.exit()

    def __usage(self, processName):
        print("Usage: {} URL  Path".format(processName))
        print("For example:")
        print("     ...")

    def myPrint(self):
        print("debug    : ", self.debug )
        print("enter_url: ", self.enter_url)
        print("save_path: ", self.save_path)



class mdprPhoto(object):
    def __init__(self, para):
        self.debug = para.debug
        self.img_dir = para.save_path.strip()
        self.ent_url = para.enter_url.strip()

    def GetMsgEx(self, url, para=None, cookies=None, data=None, filename=None):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Connection': 'keep-alive'}
        if para:
            for key in para.keys():
                if para[key] is None:
                    del para[key]
                else:
                    headers[key] = para[key]
        if cookies and len(cookies) != 0:
            headers['cookie'] = cookies
        try:
            response = response.post(url, headers=headers, data=data) if data else requests.get(url, headers=headers)
        except Exception as e:
            print(e)
            return None

        if str(response.status_code)[0] != '2':
            print("HTTP error, status_code is %s,  url=%s"%(response.status_code, url))
            return None
        if filename:
            with open(filename, 'wb') as fd:
                for response_data in response.iter_content(1024):
                    fd.write(response_data)
            return filename
        else:
            return response.text

    def get_imgUrls(self):
        if not self.ent_url:
            print("NO url to request!")
            return None

        headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'}

        response = self.GetMsgEx(self.ent_url, headers)
        if not response:
            print("request enter_url[%s] error!" % self.ent_url)
            return None

        try:
            soup = BeautifulSoup(response, 'html.parser')
            content_photo = soup.find('div', {'class': 'content-photo clearfix'})
        except Exception as e:
            print(e)
            return None

        img_urls = []
        img_urls = ['http://mdpr.jp' + figure.a['href'].strip() for figure in content_photo.findAll('figure', {"class":"square"})]
        if self.debug:
            print(img_urls)
        return img_urls

    def get_img(self, img_url):
        response = self.GetMsgEx(img_url.strip())
        if not response:
            print("request img_url[%s] error!" % img_url)
            return None

        try:
            soup = BeautifulSoup(response, 'html.parser')
            main_photo = soup.find('figure', {"class":"main-photo f9em"})
            img_src = main_photo.find('img')['src'].strip()
        except Exception as e:
            print("BeautifulSoup analyse img_src error!")
            return None

        ''' get img name'''
        img_name_tmp = img_src.split('/')[-1]
        img_name = img_name_tmp.split('?')[0]
        img_path = self.img_dir + img_name.strip()

        filename = self.GetMsgEx(img_src, filename=img_path)
        if not filename:
            print("get img_src[%s] failed!"%img_src)
            return None
        if self.debug:
            print("img_url: ", img_url)
            print("img_src: ", img_src)
        return filename


def main():
    time_start = time.time()

    para = DealWithArgv(debug=0)
    para.myPrint()

    mdpr = mdprPhoto(para)

    img_urls = mdpr.get_imgUrls()
    if not img_urls:
        print("get  img_urls list failed!!!")
        sys.exit()
    pool = Pool(15)
    filenames = pool.map(mdpr.get_img, img_urls)
    pool.close()
    pool.join()

    time_end = time.time()
    print("Lasted %d seconds" % (time_end-time_start))


if __name__ == "__main__":
    main()