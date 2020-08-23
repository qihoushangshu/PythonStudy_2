from selenium import webdriver
import time
import re
import requests
from urllib.parse import urlparse
from lxml import etree
import random
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}

#使用selenium在百度自动搜索小说
def selenium_main(story):
    # 声明
    option = webdriver.ChromeOptions();
    # chrome正受到自动测试软件的控制对应
    option.add_experimental_option("excludeSwitches", ['enable-automation']);
    driver = webdriver.Chrome(options=option);
    # 打开百度
    driver.get('http://www.baidu.com');
    # 输入搜做关键字
    driver.find_element_by_id("kw").send_keys(story);
    # 点击百度一下按钮
    driver.find_element_by_id("su").click();
    # 休眠一下
    time.sleep(2);
    # 打开百度搜到的地址
    open_url(driver,story);


# 在百度一览里，找到笔趣阁的网站，并打开
def open_url(driver,story):
    # 在百度一览里的前5条里，搜寻笔趣阁的小说网址
    # 初期化1
    indexStr = "1";
    # 初期化false
    flag = False;
    for index in range(1, 6):
        # int转字符串
        indexStr = str(index);
        # 从id=1开始到id=5，获取a标签的内容
        title = driver.find_element_by_id(indexStr).find_element_by_tag_name("a").text
        #  查找标题里包含笔趣阁字样的第一条数据，退出循环
        if title.find("笔趣阁", 0, len(title)) != -1:
            print(title);
            flag = True;
            break;
    # 如果在一览里没有找到包含笔趣阁的标题，返回9
    if not flag and indexStr == "1":
        return "9";
    #  点击标题里包含笔趣阁文字的链接
    driver.find_element_by_id(indexStr).find_element_by_tag_name("a").click();
    # 取得所有窗口的handles
    handles = driver.window_handles;
    # 切换到新打开的tab页里
    driver.switch_to.window(handles[-1]);
    # 休眠
    time.sleep(2);
    # 取得当前tab网页的url
    currentUrl = driver.current_url;
    # http://www.biquge.info/47_47063/
    # https://www.biqumo.com/2_2730/
    # http://www.xbiquge.la/45/45587/
    print(currentUrl);
    # 判断是哪个url并调用爬虫
    switch_url(currentUrl,driver,story);

    # if res is not None:
    #     if res.group() == "http://www.biquge.info":
    #         biquge.spider_biquge_story(url)
    #     elif res.group() == "http://www.xbiquge.la":
    #         xinbiquge.spider_biquge_story(url)
    #     else:
    #         print("没有检索到")
    # else:
    #     driver.switch_to.window(handles[0])
    #     return flag
    driver.quit()


# http://www.biquge.info/47_47063/
# https://www.biqumo.com/2_2730/
# http://www.xbiquge.la/45/45587/
# 判断是哪个url并调用
def switch_url(currentUrl,driver,story):
    # [a-zA-z]+://[^\s]*
    # 匹配上记三个网址
    res = re.match("[a-zA-z]+://.*?[biquge|xbiquge|biqumo].*", currentUrl, re.I);
    # print(res)
    # print("res.group()------:" + res.group())
    try:
        # 如果是三个网站之一，执行if语句
        if res is not None:
            # 取得各自网站的关键字
            reContent = re.search(".*?(biquge|xbiquge|biqumo).*",res.group(),re.I);
            print("reContent:-------------:"+reContent.group(1))
            reContentStr = reContent.group(1);
            if "biquge"== reContentStr:
                # biquge
                # 开始调用爬取
                spider_story(currentUrl,1,story);
            elif "xbiquge" == reContentStr:
                # xbiquge
                # 开始调用爬取
                spider_story(currentUrl,2,story);
            else:
                # biqumo
                # 开始调用爬取
                spider_story(currentUrl,3,story);
        else:
            return "9";
    except:
        print("正则表达式判断出错！");
        driver.quit();
        return "9";

def spider_story(currenturl,num,story):
    #根网址
    base_url = '%s' % currenturl;
    try:
        # 取得整个页面html
        html_str = spider_url(base_url, header);
        #print(html_str);
        # //*[@id="list"]/dl/dd[1]/a
        # 拿到html_str后就可以使用etree.HTML()方法获取html对象，之后就可以使用xpath方法了
        html = etree.HTML(html_str)  # <Element html at 0x7ff3fe0d6108>

        old_url = base_url;
        sub_header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'Referer': '%s' % old_url
        }
        if 1 == num:
            # biquge
            url_list_1_2 = html.xpath('//*[@id="list"]/dl/dd[*]/a');
            for obj in url_list_1_2:
                # /2_2730/6967027.html----第1221章 大结局
                print(obj.attrib['href']+'----'+obj.text);
                new_url = base_url + obj.attrib['href']
                # 爬取文章内容
                responseText = spider_url(new_url, header);
                #//*[@id="content"]/text()
                sub_html = etree.HTML(responseText)
                # 提取文章的内容
                contents = sub_html.xpath('//*[@id="content"]/text()')
                # print("contents:    "+contents);
                # 写入文件标题
                write_txt(story + ".txt", obj.text);
                for story_line in contents:
                    # 写入文件每行的内容
                    write_txt(story + ".txt", story_line);
                old_url = new_url
                # 模拟用户浏览，设置一个爬虫间隔，防止ip被封
                time.sleep(random.random() * 5)
        elif 2 == num:
            # xbiquge
            url_list_1_2 = html.xpath('//*[@id="list"]/dl/dd[*]/a');
            for obj in url_list_1_2:
                # print(obj.attrib['href'] + '----' + obj.text);
                parsed = urlparse(base_url);
                scheme = parsed.scheme;
                # 取得根网址：www.biqumo.com
                netloc = parsed.netloc;
                # print(scheme+"=============="+netloc);
                # url做成
                new_url = scheme + "://" + netloc + obj.attrib['href']
                # 爬取文章内容
                responseText = spider_url(new_url, header);
                # //*[@id="content"]/text()
                sub_html = etree.HTML(responseText)
                # 提取文章的内容
                contents = sub_html.xpath('//*[@id="content"]/text()')
                print("title  :    "+obj.text);
                # 写入文件标题
                write_txt(story + ".txt", obj.text);
                for story_line in contents:
                    # 写入文件每行的内容
                    write_txt(story + ".txt", story_line);
                old_url = new_url
                # 模拟用户浏览，设置一个爬虫间隔，防止ip被封
                time.sleep(random.random() * 5)
        else:
            # biqumo /html/body/div[5]/dl/dd[13]/a
            url_list_3 = html.xpath("/html/body/div[@class='listmain']/dl/dd[*]/a");
            parsed = urlparse(base_url);
            scheme = parsed.scheme;
            #取得根网址：www.biqumo.com
            netloc = parsed.netloc;
            #print(scheme+"=============="+netloc);
            counter = 1;
            for obj in url_list_3:
                # /2_2730/6967027.html----第1221章 大结局
                # print(obj.attrib['href']+'----'+obj.text);
                new_url = scheme +"://"+netloc + obj.attrib['href']
                # 爬取文章内容
                responseText = spider_url(new_url, header);
                #//*[@id="content"]/text()
                sub_html = etree.HTML(responseText)
                # 提取文章的内容
                contents = sub_html.xpath('//*[@id="content"]/text()')
                # print("contents:    "+contents);
                # 前12条是最新章节，pass掉
                if counter > 12:
                    # 写入文件标题
                    write_txt(story + ".txt", obj.text);
                    for story_line in contents:
                        # 写入文件每行的内容
                        write_txt(story + ".txt", story_line);
                counter += 1;
                old_url = new_url
                # 模拟用户浏览，设置一个爬虫间隔，防止ip被封
                time.sleep(random.random() * 5)
    except Exception as e:
        print('爬取失败',e);

#取得整个页面html
def spider_url(base_url,header):
    response = requests.get(base_url,headers=header);
    #chardet的编码检测
    response.encoding = response.apparent_encoding;
    response.raise_for_status();
    return response.text;


def write_txt(file_name,content):
    with open(file_name, 'a+') as file:
        # 过滤掉内容是换行符的内容
        if content != "\n" and content != "\r":
            # 过滤每行的内容里包含的换行符
            content = re.sub('\n|\r','',content);
            file.write(content + '\n')


if __name__ == '__main__':
    # selenium_main("春秋我为王")
    # selenium_main("秦吏")
    selenium_main("汉阙")
    print('爬取完成')
