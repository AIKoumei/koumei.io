# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 14:12:04 2022

@author: Koumei
"""

#HTTP请求
import urllib
import urllib.request
import requests
import gzip
import zipfile
#正则表达式
import re
#文件
import os, sys
import io
import shutil
import ctypes
import json

from tqdm import tqdm

# 第二种爬虫，浏览器爬虫
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By

# 第三种，第三方库
# os.system(you-get --format=mp4hd url)

base_url_bili = 'https://www.bilibili.com/video'
path_bili_download = 'G:/Download/bilibili'
path_rename_output = 'G:/Download/bilibili.rename.output'


header = {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                       'AppleWebKit/537.36(KHTML, like Gecko) '
                       'Chrome/67.0.3396.99 Mobile Safari/537.36'}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
if not is_admin():
    print("无管理员权限")
    # ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

#发送请求并返回获取到的HTML数据(字符串)
def GetHTML(url, is_gzip = False):
    #伪装浏览器请求头
    header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75'}
    #使用传入的url创建一个请求
    request = urllib.request.Request(url, headers = header)
    #发送请求并得到响应
    response = urllib.request.urlopen(request)
    
    if is_gzip :
        return gzip.GzipFile(fileobj = io.BytesIO(response.read())).read().decode('utf-8')
    
    #获取通过utf-8格式解码后的HTML数据
    HTML = response.read().decode('utf-8')
    #返回HTML数据
    return HTML


# print(GetHTML(base_url_bili))


#从HTML数据中匹配出所有标题
def GetTitles(HTML):
    #通过正则表达式创建一个正则匹配模式
    pattern = re.compile('<h1.*?class="video-title.*?".*?>(.*?)</h1>')
    #得到所有匹配结果，findall的返回值类型为列表
    titles = re.findall(pattern, HTML)
    #返回所有标题内容
    return titles


#从HTML数据中匹配出所有标题
def get_mutli_page(HTML):
    #通过正则表达式创建一个正则匹配模式
    pattern = re.compile('<div.*?id="multi_page".*?>.*?<span class="cur-page">\((.*?)\)</span>.*?</div>')
    #得到所有匹配结果，findall的返回值类型为列表
    result = re.findall(pattern, HTML)
    #返回所有标题内容
    return result and result[0] and result[0].split('/') or False


def get_multi_page_content(HTML):
    pattern = re.compile('<div class="cur-list".*?>(.*?)</div>')
    result = re.findall(pattern, HTML)
    return result


#将数据保存到文件
def SaveData_alter(data):
    #判断一个文件夹是否存在
    flag = os.path.exists('title')
    if not flag:
        #不存在则新建一个文件夹
        os.mkdir('title')
        print('文件夹','title','创建成功')
    else:
        print('文件夹','title','已存在')
    #将列表中的数据写入文件并保存在文件夹中
    i = 0
    for title in data:
        #打开文件时在文件名前加上文件夹路径
        file = open('title/'+'标题'+str(i)+'.txt', 'w')
        file.write(title)
        file.close()
        print('标题',str(i),'写入成功！')
        i += 1
        

#暂停一下
# pause = input('任意键退出')


# print(GetTitles(GetHTML(base_url_bili)))

def rename_file(key, page, name):
    return

def read_data_folder():
    #文件的读操作
    titles_dict = {}
    with open(path_bili_download + '/data.txt','r') as f:
        for line in f.readlines():
            d = line.split(" ")
            titles_dict[str(d[0])] = d[1]
    print(titles_dict)

def test_():
    for key in titles_dict:
        bv = titles_dict[key]
        url = base_url_bili + "//" + bv
        print(url)
        html = GetHTML(url, is_gzip = True)
        # print(html)
        # 获取有多少集
        m = get_mutli_page(html)
        # 如果是多集，批量重命名
        if m :
            # print(get_multi_page_content(html))
            num = int(m[1])
            for i in range(1,num+1):
                break

def get_mp4_file(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            file_ext = os.path.splitext(f)[-1]
            if file_ext == '.mp4':
                return os.path.join(root, f)
    return False


def parse():
    #
    option = ChromeOptions()
    option.add_argument('--headless')
    browser = webdriver.Chrome(options=option)
    browser.implicitly_wait(10)
    #
    p_list = []
    title_list = []
    for key in titles_dict:
        bv = titles_dict[key]
        url = base_url_bili + "/" + bv
        print(url)

        browser.get(url)
        table = browser.find_element(by=By.CSS_SELECTOR, value=".cur-list")
        p_nums = table.find_elements(by=By.CLASS_NAME, value="page-num")
        p_titles = table.find_elements(by=By.CLASS_NAME, value="part")
        for num in p_nums:
            p_list.append(num.text)
        for title in p_titles:
            title_list.append(title.text)
        # print(p_list)
        # print(title_list)
        
        video_title = browser.find_element(by=By.CLASS_NAME, value="video-title")
        video_title = video_title.text
        print(video_title)

        p_num = browser.find_element(by=By.CLASS_NAME, value="cur-page")
        p_num = p_num.text[1:-1].split("/")
    
        # 判断一个文件夹是否存在
        path_exists = os.path.exists(path_rename_output)
        if not path_exists:
            # 不存在则新建一个文件夹
            os.mkdir(path_rename_output)
        output_video_path = path_rename_output + "/" + video_title
        path_exists = os.path.exists(output_video_path)
        if not path_exists:
            # 不存在则新建一个文件夹
            os.mkdir(output_video_path)
            
        # 将列表中的数据写入文件并保存在文件夹中
        # i = 0
        # for p in p_nums:
        #     i += 1
        #     origin_path = "/".join([path_bili_download, key, str(i)])
        #     print(origin_path)
        #     print('> 开始处理第{}个文件，{}：{}'.format(i, p_nums[i].text, p_titles[i].text))

        #     if not os.path.exists(origin_path):
        #         continue
        #     print(origin_path)
        #     mp4_file = get_mp4_file(origin_path)
        #     if not mp4_file:
        #         continue
            
        #     # output_mp4_file = output_video_path + "/" +  p_titles[i].text + ".mp4"
        #     output_mp4_file = "{}/{}：{}.mp4".format(output_video_path, p_nums[i-1].text, p_titles[i-1].text)
        #     print(mp4_file)
        #     print(output_mp4_file)
        #     if not os.path.exists(output_mp4_file):
        #         shutil.copyfile(mp4_file, output_mp4_file)
        #     break
            
        
        # i = 0
        # for title in data:
        #     # 打开文件时在文件名前加上文件夹路径
        #     file = open('title/'+'标题'+str(i)+'.txt', 'w')
        #     file.write(title)
        #     file.close()
        #     print('标题',str(i),'写入成功！')
        #     i += 1
        
        
        # 第三方
        print("开始第三方下载")
        print(url)
        # cmd = "you-get -o {} --format=dash-flv --playlist  {}".format(output_video_path, url)
        cmd = "you-get -o {} --playlist  {}".format(output_video_path, url)
        print(cmd)
        os.system(cmd)


# parse()

def check_chromedrive_version():
    # 获取项目根路径
    root_path = os.path.abspath(os.path.dirname(__file__))
    download_path = root_path + "/download"  # 这里需要提前手动创建号download目录
    # print(root_path)
    try:
        option = ChromeOptions()
        option.add_argument('--headless')
        browser = webdriver.Chrome(options=option)
    except Exception as msg:
        # print("ChromeWebDriver异常：" + str(msg))
        old_chromedriver_version = re.search("Chrome version \d+", str(msg)).group().replace("Current browser version is ", "")

        reg = "Current browser version is.+with"
        chrome_version = re.search(reg, str(msg)).group().replace("Current browser version is ", "").replace(" with","")
        print("Chrome Version:" + chrome_version)
        
        html = GetHTML("http://chromedriver.storage.googleapis.com/")
        chrome_sub_version = ".".join(chrome_version.split(".")[0:3])
        print("chrome_sub_version:" + chrome_sub_version)
        all_version = re.findall(f"<Key>{chrome_sub_version}.*?</Key>", str(html))

        version_sub_download_url = []
        for version in all_version:
            result = re.search("win32", version)
            if result :
                version_sub_download_url.append(version.replace("<Key>", "").replace("</Key>", ""))
        version_sub_download_url.sort()
        print(f"get chromedriver version:{version_sub_download_url}")

        url = "http://chromedriver.storage.googleapis.com/" + version_sub_download_url[-1]
        download_version = version_sub_download_url[-1].split("/")[0]
        file_name = download_path + "/chromedriver_" + download_version + ".zip"
        print("download chromedriver url :" + url)
        response = requests.get(url)

        # 使用代理
        # proxy = xxx.xxx.x.xx:8080
        # proxies = {
          
   
        #     http: http:// + proxy,
        #     https: https:// + proxy
        # }
        # response = requests.get(url=url, proxies=proxies)

        # 使用PAC自动代理
        # pac = get_pac(url=http://xxx.xxx.x.xx:8080/xxx.pac)
        # pac_session = PACSession(pac)  # 解析pac文件
        # response = pac_session.get(url)

        # 保存ChromeDriver到当前项目路径下的/download目录下
        with open(file_name, "wb") as file:
            file.write(response.content)
        zf = zipfile.ZipFile(file_name)
        extra_path = f"{download_path}/chromedriver_{download_version}"
        zf.extractall(path=extra_path)
        # import admin
        # if not admin.isUserAdmin():
        #     admin.runAsAdmin()
        shutil.copyfile(f"{extra_path}/chromedriver.exe", "C:/Program Files/Google/Chrome/Application/chromedriver.exe")
        # cmd = f'start cmd /k copy  \"{extra_path}\\chromedriver.exe\" \"C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe\"'
        # print(f"cmd:{cmd}")
        # os.system(cmd)
check_chromedrive_version()
# cmd = "start cmd /k copy \"E:\\workspace.script\\web_monitor\\download\\chromedriver_111.0.5563.64\\chromedriver.exe\" \"C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe\" "
# print(cmd)
# os.system(cmd)


def monitor_url():
    BASE_URL = 'https://www.bookmarkearth.com'
    PARAM = '/page?currentPage='


    
    # html = GetHTML(URL, is_gzip=False)
    # print(html)

    option = ChromeOptions()
    option.add_argument('--headless')
    browser = webdriver.Chrome(options=option)
    browser.implicitly_wait(10)

    page_total_num = 0

    browser.get(BASE_URL)
    page_tables = browser.find_element(by=By.CLASS_NAME, value="pager").find_elements(by=By.TAG_NAME, value="li")
    for page_item in page_tables:
        text = page_item.text
        if text.startswith('当前'):
            try:
                num = text.replace("当前 ", "").replace("页", "").split("/")[1]
                page_total_num = int(num)
            except Exception as msg:
                print(msg)
    print(f"获取总页数：{page_total_num}")
    if page_total_num == 0:
        return

    tabs_info = []
    for i in tqdm(range(1, page_total_num + 1)):
        page_num = i
        PAGE_URL = f"{BASE_URL}{PARAM}{page_num}"
        print(f"\n访问地址:{PAGE_URL}")
        
        browser.get(PAGE_URL)
        tab_tables = browser.find_elements(by=By.CLASS_NAME, value="document-piece")
        for tab in tab_tables:
            tab_info = {}
            tabs_info.append(tab_info)
            tab_info["username"] = tab.find_element(by=By.CLASS_NAME, value="username").text
            info_tables = tab.find_elements(by=By.CLASS_NAME, value="info-label")
            for info in info_tables:
                info_text = info.text.strip()
                if info_text.startswith("大小："):
                    tab_info["size"] = info_text.split("大小：")[-1]
                    kb = float(info_text.split("大小：")[-1].split(" ")[0])
                    if tab_info["size"].endswith("KB"):
                        tab_info["size_kb"] = kb
                    elif tab_info["size"].endswith("MB"):
                        tab_info["size_kb"] = kb * 1024
                    elif tab_info["size"].endswith(" B"):
                        tab_info["size_kb"] = kb
                    else:
                        tab_info["size_kb"] = kb * 1024 * 1024
                elif info_text.startswith("网址数："):
                    tab_info["link_nums"] = info_text.split("网址数：")[-1]
                else:
                    tab_info["updated_time"] = info_text
            tab_id = tab.find_element(by=By.CLASS_NAME, value="write-user-operation").get_attribute("data-identification")
            tab_info["link"] = f"https://www.bookmarkearth.com/detail/{tab_id}"
        tabs_info.sort(key=lambda d:d["size_kb"], reverse=True)

    with open('./json.www.bookmarkearth.com.json', 'w', encoding='utf8') as json_file:
        json.dump(tabs_info, json_file, indent=4, ensure_ascii=False)

        

    # card_list = []
    # for sms_card in tables:
    #     card = {}
    #     card_list.append(card)
    #     # print(sms_card.text)
    #     card["country"] = sms_card.find_element(by=By.CLASS_NAME, value="pager").text
    #     card["link"] = sms_card.find_element(by=By.CLASS_NAME, value="sms-card__header").get_attribute('href')
    #     card["number"] = sms_card.find_element(by=By.CLASS_NAME, value="sms-card__number").find_element(by=By.TAG_NAME, value="a").text
    #     items = sms_card.find_elements(by=By.CLASS_NAME, value="sms-card__item")
    #     for item in items:
    #         title = item.find_element(by=By.CSS_SELECTOR, value=".text.text--light").text
    #         text = item.find_element(by=By.CSS_SELECTOR, value=".text.text--bold").text
    #         card[title] = text
    # print(card_list)
    # with open('./card.json', 'w', encoding='utf8') as json_file:
    #     json.dump(card_list, json_file, indent=4, ensure_ascii=False)

monitor_url()
# input('enter')

# test_url = "https://www.bilibili.com/video/BV1vm4y1R7yV"
# test_url = "https://www.bilibili.com/video/BV1ZZ4y1R7H7"
# os.system("you-get -i --playlist {}".format(test_url))
# --playlist

# def simple_rename():
    


