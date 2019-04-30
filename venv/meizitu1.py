import gevent  #导入协程的模块，没有需要先行安装
from lxml import etree  #导入xml xpath的相关模块，没有的先行安装
import os,threading  #导入os模块 导入多线程模块
import urllib.request  #导入网络爬取模块
import time

# 请求头的配置
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.9 (KHTML, like Gecko) Chrome/ Safari/530.9 '
}
# 需要爬取的基础url
baseurl = 'http://www.meizitu.com/a/more'
'''
分析：
先获取需要下载的更过页面是几页，然后获取这里面的所有第二级url
然后在爬取这些url里面的图片进行下载
'''
# //div[@class="pic"]/a/@href      获取页面所有URL
# //div[@id="picture"]/p/img/@alt  获取图片名称
# //div[@id="picture"]/p/img/@src  获取图片路径
# 下载图片的函数
def download_img(image_url_list,image_name_list,image_fenye_path):
    try:
        # 创建每个页保存的目录
        os.mkdir(image_fenye_path)
    except Exception as e:
        pass
    for i in range(len(image_url_list)):
        # 获取图片后缀
        houzhui = (os.path.splitext(image_url_list[i]))[-1]
        # 拼接文件名
        file_name = image_name_list[i] + houzhui
        # 拼接文件保存路径
        save_path = os.path.join(image_fenye_path,file_name)
        # 开始下载图片
        print(image_url_list[i])
        try:
            # 发现这里读取不了，一次改为文件读写
            # urllib.request.urlretrieve(image_url_list[i],save_path)
            newrequest = urllib.request.Request(url=image_url_list[i], headers=headers)
            newresponse = urllib.request.urlopen(newrequest)
            data = newresponse.read()
            with open(save_path,'wb') as f:  #with写法
                # f = open('test.jpg', 'wb')  原始的写法
                f.write(data)
                f.close()
            print('%s 下载完毕'%save_path)
        except Exception as e:
            print('%s xxxxxxxx图片丢失'%save_path)

# 获取url的函数
def read_get_url(sure_url,image_fenye_path):
    request = urllib.request.Request(url=sure_url, headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read().decode('gbk')
    html_tree = etree.HTML(html)
    need_url_list = html_tree.xpath('//div[@class="pic"]/a/@href')
    # print(need_url_list)
    # 每个线程内部开启协程爬取下载
    xiecheng = []
    for down_url in need_url_list:
        # 创建协程处理对象
        xiecheng.append(gevent.spawn(down_load, down_url,image_fenye_path))
    # 开启协程
    gevent.joinall(xiecheng)

# 中间处理函数
def down_load(read_url,image_fenye_path):
    # print(read_url,image_fenye_path)
    try:
        request = urllib.request.Request(url=read_url, headers=headers)
        response = urllib.request.urlopen(request)
        html = response.read().decode('gbk')
        html_tree = etree.HTML(html)
        # 获取图片的名称
        image_name_list = html_tree.xpath('//div[@id="picture"]/p/img/@alt')
        # 获取图片的url
        image_url_list = html_tree.xpath('//div[@id="picture"]/p/img/@src')
        # print(image_url_list,image_name_list)
        download_img(image_url_list,image_name_list,image_fenye_path)
    except Exception as e:
        pass

# 主要入口函数
def main(baseurl):
    start_page = int(input('请输入起始页面：'))
    end_page = int(input('请输入结束页面：'))
    # 创建保存的文件夹
    try:
        global father_path
        # 获取当前文件的目录名
        father_path = (os.path.dirname(os.path.abspath(__file__)))
        # 创建一个目录用于保存图片
        mkdir_name = father_path + '/meizitufiles'
        os.mkdir(mkdir_name)
    except Exception as e:
        print(e)
    print('开始下载...')
    t_list = []
    # 每个页面开启一个线程
    for page_num in range(start_page,end_page + 1):
        # 拼接url
        sure_url = baseurl + '_' + str(page_num) + '.html'
        # 获得每一页的目录名
        image_fenye_path = father_path + '/meizitufiles' + '/第%s页'%page_num
        t = threading.Thread(target=read_get_url,args=(sure_url,image_fenye_path))
        t.start()
        t_list.append(t)
    for j in t_list:
        j.join()
    print('下载完毕！')

if __name__ == '__main__':
    start_time = time.time()
    main(baseurl)
    print('最终下载时间为：%s'%(time.time()-start_time))