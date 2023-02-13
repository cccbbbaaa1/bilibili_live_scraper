import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
import pandas as pd
import datetime
from threading import Timer
import os

game_list = ['dreadhunger','英雄杀','三国杀','qq飞车']  # 设置游戏名列表
game_list_douyu = ['EFT','Cyberpunk','DW','hydbk','DNF']
game_list_huya = ['6149','7601','5011','6219','1732']
save_path = r"D:/科研/游戏直播/Bilibili-Live-Message-master/data/"

# B站爬取主函数
def bilibili_scratch(search_key):
    # 抓取直播间url、id、直播间名字、主播名字、人气 + 游戏名

    # 打开网页
    url = 'https://search.bilibili.com/live?keyword='+ str(search_key)
    opt = Options()
    # 删掉Chrome浏览器正在受到自动测试软件的控制
    opt.add_experimental_option('excludeSwitches',['enable-automation'])
    opt.add_argument('--headless')
    # 创建浏览器对象
    web = Chrome(options=opt)
    web.get(url)
    error_count = 0
    #web.implicitly_wait(2)
    time.sleep(1)
    #div_list = web.find_elements_by_xpath('//*[@id="app"]/div[1]/div[1]/div')
    live_dic = {}
    end = 1 # 设置停止翻页指标
    while end:
        # sum_div = web.find_elements(By.CLASS_NAME,"ml_md fs_4 text3 fw_400")  # 总计直播间数
        # print(sum_div)
        div_list = web.find_elements(By.CLASS_NAME,"video-list-item.col_3.col_xs_1_5.col_md_2.col_xl_1_7.mb_xxl")
        # 出错判断
        if len(div_list) == 0:
            web.refresh()
            time.sleep(2)
            div_list = web.find_elements(By.CLASS_NAME, "video-list-item.col_3.col_xs_1_5.col_md_2.col_xl_1_7.mb_xxl")
        #print(len(div_list))

        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1] 直播间div
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[3]/div/div[1]/div/div[2]/a"  直播间url
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/h3/a/span   直播间名字
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/a/span  主播名字
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/a/div/div[1]/div/span  人气值
        for div in div_list:
            try:
                # 定位直播间url
                url = div.find_element(By.XPATH,'./div/div[2]/a').get_attribute(
                    'href')
                # print(url)
                live_name = div.find_element(By.XPATH,'./div/div[2]/div/div/h3/a/span').text
                if live_name == '':
                    continue
                #print(live_name)
                liver = div.find_element(By.XPATH,'./div/div[2]/div/div/a/span').text  # 定位直播间名字
                hot = deal_num(div.find_element(By.XPATH, './div/div[2]/a/div/div[1]/div/span').text)  # 定位直播间人气
                # 通过直播间url提取直播间id
                obj1 = re.compile(r"com/(?P<id>\d+)", re.S)
                live_id = obj1.finditer(url)
                for i in live_id:
                    #print("live id : ", i.group("id"))
                    id = i.group("id")
                # 直播间名字//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/h3/a/span
                live_dic[id] = [search_key,hot,url,liver,live_name]
            except:
                error_count += 1
                print("WARNING : Can not find!")
        # 进行翻页
        try:
            web.execute_script('window.scrollTo(0,document.body.scrollHeight)')  # 滚动
            botton = web.find_elements(By.CSS_SELECTOR, ".vui_button.vui_pagenation--btn.vui_pagenation--btn-side")[
                1]  # 点击下一页按钮
            if botton.is_enabled():  # 判断按钮是否激活，即是否末页
                botton.click()
            else:
                end = 0
            time.sleep(2)
        except:
            end = 0
        # if len(live_dic) >= live_room_count :
        #     end = 0
    try:
        # 总直播间数
        live_room_count = (web.find_element(By.XPATH,
                                            '//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/h1/span/span').text)
        obj = re.compile(r"\d+")
        live_room_count = deal_num(obj.findall(live_room_count)[0])
        # 总直播间热度
        # live_hot_count = deal_num(web.find_element(By.XPATH, '/html/body/section/main/section[1]/div[3]/span[1]/em').text)
        # print(live_hot_count)
    except:
        live_room_count = 'Nan'
    live_hot_count = 0
    for i in live_dic:
        live_hot_count += live_dic[i][1]
    return [live_dic,error_count,len(live_dic),live_room_count,live_hot_count]


# 斗鱼爬取主函数
def douyu_scratch(search_key):
    # 抓取直播间url、id、直播间名字、主播名字、人气 + 游戏名
    # 打开网页
    url = 'https://www.douyu.com/g_' + search_key
    opt = Options()
    # 删掉Chrome浏览器正在受到自动测试软件的控制
    opt.add_experimental_option('excludeSwitches',['enable-automation'])
    opt.add_argument('--headless')
    # 创建浏览器对象
    web = Chrome(options=opt)
    web.get(url)
    error_count = 0
    web.execute_script('window.scrollTo(0,document.body.scrollHeight)')  # 滚动
    time.sleep(4)
    live_dic = {}
    end = 1  # 设置停止翻页指标
    while end:
        # sum_div = web.find_elements(By.CLASS_NAME,"ml_md fs_4 text3 fw_400")  # 总计直播间数
        # print(sum_div)
        div_list = web.find_elements(By.CLASS_NAME,"layout-Cover-item")
        # 出错判断
        if len(div_list) == 0:
            web.refresh()
            time.sleep(2)
            div_list = web.find_elements(By.CLASS_NAME, "layout-Cover-item")
        #print(len(div_list))

        # /html/body/section/main/section[2]/div[2]/ul/li[1] 直播间div
        # /html/body/section/main/section[2]/div[2]/ul/li[1]/div/a  直播间url
        # /html/body/section/main/section[2]/div[2]/ul/li[1]/div/a/div[2]/div[1]/h3   直播间名字
        # /html/body/section/main/section[2]/div[2]/ul/li[1]/div/a/div[2]/div[2]/h2/div  主播名字
        # /html/body/section/main/section[2]/div[2]/ul/li[1]/div/a/div[2]/div[2]/span  人气值
        for div in div_list:
            try:
                # 判断是不是视频
                video = div.find_elements(By.CLASS_NAME,'DyListCover-watchNumer')
                if len(video)>=1:
                    continue
                # 定位直播间url
                url = div.find_element(By.XPATH,'./div/a').get_attribute(
                    'href')
                #print(url)
                live_name = div.find_element(By.CLASS_NAME,'DyListCover-intro').text
                if live_name == '':
                    continue
                #print(live_name)
                liver = div.find_element(By.CLASS_NAME,'DyListCover-userName').text  # 定位主播名字
                hot = deal_num(div.find_element(By.CLASS_NAME, 'DyListCover-hot').text)  # 定位直播间人气
                # print(liver,hot)
                # 通过直播间url提取直播间id
                obj1 = re.compile(r"com/(?P<id>\d+)", re.S)
                live_id = obj1.finditer(url)
                for i in live_id:
                    #print("live id : ", i.group("id"))
                    id = i.group("id")
                # 直播间名字//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/h3/a/span
                live_dic[id] = [search_key,hot,url,liver,live_name]
            except:
                error_count += 1
                print("WARNING : Can not find!")
        # 进行翻页
        try:
            last_page_bot = web.find_elements(By.CLASS_NAME,"dy-Pagination-disabled.dy-Pagination-next")  # 判断最后一页
            if len(last_page_bot) == 1:
                end = 0
            web.execute_script('window.scrollTo(0,document.body.scrollHeight)')  # 滚动
            botton = web.find_elements(By.CLASS_NAME,"dy-Pagination-item-custom")[1] # 点击下一页按钮
            if botton.is_enabled():  # 判断按钮是否激活，即是否末页
                botton.click()
            else:
                end = 0
            time.sleep(2)
            #web.implicitly_wait(5)
        except:
            end = 0
        # if len(live_dic) >= live_room_count :
        #     end = 0
    # 获取统计信息,若无则自行计算
    try:
        # 总直播间数
        live_room_count = deal_num(web.find_element(By.XPATH, '/html/body/section/main/section[1]/div[3]/span[2]/em').text)
        # 总直播间热度
        live_hot_count = deal_num(web.find_element(By.XPATH, '/html/body/section/main/section[1]/div[3]/span[1]/em').text)
        # print(live_hot_count)
    except:
        live_room_count = len(live_dic)
        live_hot_count = 0
        for i in live_dic:
            live_hot_count += live_dic[i][1]
    return [live_dic,error_count,len(live_dic),live_room_count,live_hot_count]


# 虎牙爬取主函数
def huya_scratch(search_key):
    # 抓取直播间url、id、直播间名字、主播名字、人气 + 游戏名
    # 打开网页
    url = 'https://www.huya.com/g/' + str(search_key)
    opt = Options()
    # 删掉Chrome浏览器正在受到自动测试软件的控制
    opt.add_experimental_option('excludeSwitches',['enable-automation'])
    opt.add_argument('--headless')
    # 创建浏览器对象
    web = Chrome(options=opt)
    web.get(url)
    error_count = 0
    time.sleep(1)
    web.execute_script('window.scrollTo(0,document.body.scrollHeight)')  # 滚动
    time.sleep(1)
    #div_list = web.find_elements_by_xpath('//*[@id="app"]/div[1]/div[1]/div')
    live_dic = {}
    end = 1 # 设置停止翻页指标
    while end:
        # sum_div = web.find_elements(By.CLASS_NAME,"ml_md fs_4 text3 fw_400")  # 总计直播间数
        # print(sum_div)
        div_list = web.find_elements(By.CLASS_NAME,"game-live-item")
        # 出错判断
        if len(div_list) == 0:
            web.refresh()
            time.sleep(2)
            div_list = web.find_elements(By.CLASS_NAME, "game-live-item")
        # 总直播间人气
        #live_room_count = (web.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[2]/ul/li[1]/span/span[2]/i[2]').text)
        #obj = re.compile(r"\d+")
        #live_room_count = int(obj.findall(live_room_count)[0])
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1] 直播间div
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[3]/div/div[1]/div/div[2]/a"  直播间url
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/h3/a/span   直播间名字
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/a/span  主播名字
        # //*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/a/div/div[1]/div/span  人气值
        for div in div_list:
            try:
                # 定位直播间url
                url = div.find_element(By.XPATH,'./a[1]').get_attribute(
                    'href')
                #print(url)
                live_name = div.find_element(By.XPATH,'./a[2]').text
                if live_name == '':
                    continue
                #print(live_name)
                liver = div.find_element(By.XPATH,'./span/span[1]/i').text  # 定位直播间名字
                hot = deal_num(div.find_element(By.XPATH, './span/span[2]/i[2]').text)  # 定位直播间人气
                #print(liver,hot)
                # 通过直播间url提取直播间id
                obj1 = re.compile(r"com/(?P<id>\d+)", re.S)
                live_id = obj1.finditer(url)
                for i in live_id:
                    #print("live id : ", i.group("id"))
                    id = i.group("id")
                # 直播间名字//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/h3/a/span
                live_dic[id] = [search_key,hot,url,liver,live_name]
            except:
                error_count += 1
                print("WARNING : Can not find!")
        # 进行翻页
        try:
            web.execute_script('window.scrollTo(0,document.body.scrollHeight)')  # 滚动
            botton = web.find_element(By.CLASS_NAME, "laypage_next") # 点击下一页按钮
            botton.click()
            time.sleep(2)
        except:
            end = 0

        # if len(live_dic) >= live_room_count :
        #     end = 0
    live_room_count = len(live_dic)
    live_hot_count = 0
    for i in live_dic:
        live_hot_count += live_dic[i][1]
    return [live_dic,error_count,len(live_dic),live_room_count,live_hot_count]

# 存储结果
def start(path,live_type):
    df = pd.read_csv("game_list.csv")
    path += '/'
    game_live_count = {}
    if live_type == 'b':
        for row_index,row in df.iterrows():
            data = bilibili_scratch(row['bili_code'])
            df = pd.DataFrame.from_dict(data[0], orient='index',
                                        columns=['game', 'hot', 'url', 'liver', 'live_name']).reset_index().rename(
                columns={'index': 'id'})
            print(df.head())
            df.to_csv(path+row['game'] + '.csv')
            print(row['game'], "完成！")
            game_live_count[row['game']] = data[1:]
    elif live_type == 'd':
        for row_index,row in df.iterrows():
            data = douyu_scratch(row['douyu_code'])
            df = pd.DataFrame.from_dict(data[0], orient='index',
                                        columns=['game', 'hot', 'url', 'liver', 'live_name']).reset_index().rename(
                columns={'index': 'id'})
            print(df.head())
            df.to_csv(path+row['game'] + '.csv')
            print(row['game'], "完成！")
            game_live_count[row['game']] = data[1:]
    elif live_type == 'h':
        for row_index,row in df.iterrows():
            data = huya_scratch(row['huya_code'])
            df = pd.DataFrame.from_dict(data[0], orient='index',
                                        columns=['game', 'hot', 'url', 'liver', 'live_name']).reset_index().rename(
                columns={'index': 'id'})
            print(df.head())
            df.to_csv(path + row['game'] + '.csv')
            print(row['game'], "完成！")
            game_live_count[row['game']] = data[1:]
    df = pd.DataFrame.from_dict(game_live_count, orient='index',
                                columns=['error_count', 'record_live_num',
                                         'actual_live_room_count','total_hot_count']).reset_index().rename(
        columns={'index': 'game'})
    df.to_csv(path+'all.csv')

# 人气格式处理
def deal_num(string):
    if string[-1:] == '万':
        num = int(float(string[:-1])*10**4)
    elif string[-1:] == '亿':
        num = int(float(string[:-1])*10**8)
    else:
        try:
            num = int(string)
        except:
            num = string
    return num

# 创建文件夹
def folder_create(time_now):
    time_path = save_path + time_now
    if not os.path.exists(time_path):
        os.mkdir(time_path)
    bili_path = time_path + '/bilibili'    # B站文件夹地址
    if not os.path.exists(bili_path):
        os.mkdir(bili_path)
    douyu_path = time_path + '/douyu'    # 斗鱼文件夹地址
    if not os.path.exists(douyu_path):
        os.mkdir(douyu_path)
    huya_path = time_path + '/huya'    # 虎牙文件夹地址
    if not os.path.exists(huya_path):
        os.mkdir(huya_path)
    return [bili_path,douyu_path,huya_path]

# 设置定时执行函数
def time_printer():
    now = datetime.datetime.now()
    ts = now.strftime('%Y%m%d-%H-%M-%S')
    print('do func time :', ts)
    loop_monitor()

def loop_monitor():
    t = Timer(1800, time_printer)  # 每半小时执行一次
    t.start()
    now = datetime.datetime.now()
    ts = now.strftime('%Y%m%d-%H%M')
    path_list = folder_create(ts)
    start(path_list[0], 'b')  # b站
    start(path_list[1],'d')  # 斗鱼
    start(path_list[2], 'h')  # 虎牙

    ts = now.strftime('%Y%m%d-%H%M')
    print("finish time :",ts)

if __name__ == '__main__':
    loop_monitor()



