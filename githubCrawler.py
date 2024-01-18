import requests
from bs4 import BeautifulSoup
import re	
import json
import os
import zipfile

print('begin crawler GitHub!')


def getTrendingList(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到所有项目的链接
    all_list = []
    repo_links = soup.find_all('h2', class_='h3 lh-condensed')
    for link in repo_links:
        repo_url = 'https://github.com' + link.a['href']
        all_list.append(repo_url)
    return all_list



def find_zipball_url(json_data, key_word):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == key_word:
                return value
            else:
                result = find_zipball_url(value, key_word)
                if result is not None:
                    return result
    elif isinstance(json_data, list):
        for item in json_data:
            result = find_zipball_url(item, key_word)
            if result is not None:
                return result
def getMainZipUrl(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到zipballUrl字段, 在script type="application/json"
    repo_links = soup.find_all('script', type='application/json')
    # 假设repo_links是包含"zipballUrl"内容的列表
    for link in repo_links:
        json_data = json.loads(link.string)
        result = find_zipball_url(json_data, "zipballUrl")
        if (result != None):
            return 'https://github.com' + result
    return None

def downMainZip(url, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    zip_url = getMainZipUrl(url)
    print(f'[find zip url: {zip_url}]')
    response = requests.get(zip_url)
    # match = re.search(r'https://github.com/[^/]+/([^/]+)/', url)
    match = re.search(r'\/([^\/]+)\/?$', url)
    if match:
        content = match.group(1)
        saved_dir = f'{dst_dir}/{content}.zip'
        with open(saved_dir, 'wb') as f:
            f.write(response.content)
            print(f'downloaded: {content}.zip')
    return saved_dir

def unzipMainZip(zip_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    with zipfile.ZipFile(zip_dir, 'r') as zip_ref:
        zip_ref.extractall(dst_dir)

    content = re.search(r'\/([^\/]+)\.zip$', zip_dir).group(1) # zip文件名
    # 解压的文件夹路径
    unzip_dir = f'{dst_dir}/{content}-main'
    print(f'[have unzipped: {unzip_dir}]')
    return unzip_dir

if __name__ == "__main__":
    ''' [1]. trending页面所有项目网址链接 '''
    print("\n--------------------[1]. trending页面所有项目网址链接--------------------")
    trendingList = getTrendingList('https://github.com/trending')
    trendingList = trendingList[:2] # 只获取排名第一的
    print(f'共有{len(trendingList)}个项目, 分别是：')
    list(map(lambda x: print(x), trendingList))

    ''' [2]. 每个项目下载zip ''' # url = 'https://github.com/TencentARC/PhotoMaker/archive/refs/heads/main.zip'
    print("\n------------------------[2]. 每个项目下载zip----------------------------")
    all_zip_dir = []
    save_zip_dir = os.getcwd()+"/downZip"
    for project_url in trendingList:
        saved_dir = downMainZip(project_url, save_zip_dir)
        all_zip_dir.append(saved_dir)
    print(f"\n[all downloaded zip dir]:{all_zip_dir}\n")
    
    ''' [3]. 解压每个项目的zip '''
    print("\n-----------------------[3]. 解压每个项目的zip----------------------------")
    all_unzip_dir = []
    unzip_dst_dir = os.getcwd()+"/unZip"
    for zip_dir in all_zip_dir:
        unzip_dir = unzipMainZip(zip_dir, unzip_dst_dir)
        all_unzip_dir.append(unzip_dir)
    print(f"\n[all unzipped project dir]:{all_unzip_dir}\n")
    
    ''' [4]. 读取每个项目的readme文件内容 '''
    print("\n------------------[4]. 读取每个项目的readme文件内容-----------------------")