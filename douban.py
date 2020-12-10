



import re
import requests
# import urllib.request,urllib.error
from bs4 import BeautifulSoup
import xlwt
import sqlite3

def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getdata(baseurl)
    # savexlspath = "豆瓣电影Top250.xls"
    # savexlsdata(datalist,savexlspath)
    savedbpath = "MoivesTop250.db"
    savedbdata(datalist,savedbpath)

    getdata(baseurl)
#链接
findlink = re.compile(r'<a href="(.*?)">',re.S)        #re.S使 . 包含所有的字符（换行符也在内）
#图片
findimg = re.compile(r'<img.*?src="(.*?)"',re.S)
#片名
findtitle = re.compile(r'<span class="title">(.*?)</span>')
#评分
findscore = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
#评价人数
findpernum = re.compile(r'<span>(\d*)人评价</span>')
#概况
findinq = re.compile(r'<span class="inq">(.*?)</span>', re.S)
#相关内容
findbd = re.compile(r'<p class="">(.*?)</p>',re.S)
#爬取数据
def getdata(baseurl):
    datalist = []
    for i in range(0,10):
        url = baseurl + str(i*25)
        html = askUrl(url)

        #解析网页
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_ = "item"):        #查找符合要求的字符串
            data = []    #保存一部电影的信息
            item = str(item)
            link = re.findall(findlink,item)[0]
            data.append(link)         #保存链接

            imgsrc = re.findall(findimg,item)[0]
            data.append(imgsrc)        #保存图片链接

            titles = re.findall(findtitle,item)
            if len(titles) == 2:        #保存片名
                ctitle = titles[0].replace('/','')
                data.append(ctitle)
                print(ctitle)
                otitle = titles[1].replace("/", "")
                data.append(otitle)
            else:
                title = titles[0].replace('/','')
                data.append(title)
                data.append(" ")

            score = re.findall(findscore,item)[0]
            data.append(score)            #保存评分

            pernum = re.findall(findpernum, item)[0]
            data.append(pernum)  # 添加评价人数

            bd = re.findall(findbd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)
            bd = re.sub('/',' ',bd)
            data.append(bd.strip())                 #添加概述

            inq = re.findall(findinq,item)
            if len(inq) != 0:
                inq = inq[0].replace("。","")    #去掉句号
                data.append(inq)                     #添加相关内容
            else:
                data.append(" ")              #留空
            for i in range(len(data)):
                data[i] = data[i].replace(" "," ")
            datalist.append(data)
    # print(datalist)
    return datalist

#得到指定的url的网页内容
def askUrl(url):
    headers = {
    "User-Agent": "Mozilla / 5.0(WindowsNT10.0;WOW64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 78.0.3904.108Safari / 537.36"
    }
    request = requests.get(url,params=None,headers = headers)
    request.encoding = "UTF-8"
    #request.encoding = "utf-8"
    #request = urllib.request.Request(url,headers = head)
    html = ""
    try:
        # response = urllib.request.urlopen(request)
        # html = response.read().decode("utf-8")
        html = request.text
    except requests.exceptions as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html


#保存数据
def savexlsdata(datalist,savexlspath):
    print(f"数据保存到{savexlspath}")
    book = xlwt.Workbook(encoding = "utf-8",style_compression = 0)
    sheet = book.add_sheet("豆瓣电影Top250",cell_overwrite_ok=True)
    col = ("电影详情链接","图片链接","中文名","外文名","评分","评价人数","概况","内容")
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(1,251):
        data = datalist[i-1]
        for j in range(0,8):
            sheet.write(i,j,data[j])
        print(f"第{i}条保存成功")
    book.save(savexlspath)

def savedbdata(datalist,savedbpath):
    init_db(savedbpath)
    conn = sqlite3.connect(savedbpath)
    sql = '''
        insert into MoviesTop(Movielink,Movieimgsrc,MovieCNtitle,MovieOTtitle,Moviescore, Moviescorenum
        ,Movieinq,MOviebd)
        values (?,?,?,?,?,?,?,?)
       '''
    cursor = conn.cursor()
    num = 0
    for data in datalist:
        for i in range(len(data)):
            data[i] = data[i].replace(" "," ")
          #  print(data[i])
       # print(sql)
        cursor.execute(sql,data)
        conn.commit()
        if num!=len(datalist):
            num+=1
            print(f"第{num}个数据已保存")
    print("数据保存数据库成功")
    conn.close()

def init_db(savedbpath):

    sql = '''
        create table MoviesTop
            (
            ID integer primary key autoincrement,
            Movielink text not null,
            Movieimgsrc text not null,
            MovieCNtitle varchar not null,
            MovieOTtitle varchar,
            Moviescore numeric not null,
            Moviescorenum numeric not null,
            Movieinq varchar,
            MOviebd varchar
            );
    '''
    conn = sqlite3.connect(savedbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == "__main__":    #当程序执行时
# #调用函数
    main()

