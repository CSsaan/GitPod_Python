import requests
from bs4 import BeautifulSoup
import re
import json
import os
import zipfile

# print('begin crawler GitHub!')


# def getTrendingList(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     # 找到所有项目的链接
#     all_list = []
#     repo_links = soup.find_all('h2', class_='h3 lh-condensed')
#     for link in repo_links:
#         repo_url = 'https://github.com' + link.a['href']
#         all_list.append(repo_url)
#     return all_list


# def find_zipball_url(json_data, key_word):
#     if isinstance(json_data, dict):
#         for key, value in json_data.items():
#             if key == key_word:
#                 return value
#             else:
#                 result = find_zipball_url(value, key_word)
#                 if result is not None:
#                     return result
#     elif isinstance(json_data, list):
#         for item in json_data:
#             result = find_zipball_url(item, key_word)
#             if result is not None:
#                 return result
# def getMainZipUrl(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     # 找到zipballUrl字段, 在script type="application/json"
#     repo_links = soup.find_all('script', type='application/json')
#     # 假设repo_links是包含"zipballUrl"内容的列表
#     for link in repo_links:
#         json_data = json.loads(link.string)
#         result = find_zipball_url(json_data, "zipballUrl")
#         if (result != None):
#             return 'https://github.com' + result
#     return None

# def downMainZip(url, dst_dir):
#     if not os.path.exists(dst_dir):
#         os.makedirs(dst_dir)
#     zip_url = getMainZipUrl(url)
#     print(f'[find zip url: {zip_url}]')
#     response = requests.get(zip_url)
#     # match = re.search(r'https://github.com/[^/]+/([^/]+)/', url)
#     match = re.search(r'\/([^\/]+)\/?$', url)
#     if match:
#         content = match.group(1)
#         saved_dir = f'{dst_dir}/{content}.zip'
#         with open(saved_dir, 'wb') as f:
#             f.write(response.content)
#             print(f'downloaded: {content}.zip')
#     return saved_dir

# def unzipMainZip(zip_dir, dst_dir):
#     if not os.path.exists(dst_dir):
#         os.makedirs(dst_dir)
#     with zipfile.ZipFile(zip_dir, 'r') as zip_ref:
#         zip_ref.extractall(dst_dir)

#     content = re.search(r'\/([^\/]+)\.zip$', zip_dir).group(1) # zip文件名
#     # 解压的文件夹路径
#     unzip_dir = f'{dst_dir}/{content}-main'
#     print(f'[have unzipped: {unzip_dir}]')
#     return unzip_dir

# if __name__ == "__main__":
#     ''' [1]. trending页面所有项目网址链接 '''
#     print("\n--------------------[1]. trending页面所有项目网址链接--------------------")
#     trendingList = getTrendingList('https://github.com/trending')
#     trendingList = trendingList[:2] # 只获取排名第一的
#     print(f'共有{len(trendingList)}个项目, 分别是：')
#     list(map(lambda x: print(x), trendingList))

#     ''' [2]. 每个项目下载zip ''' # url = 'https://github.com/TencentARC/PhotoMaker/archive/refs/heads/main.zip'
#     print("\n------------------------[2]. 每个项目下载zip----------------------------")
#     all_zip_dir = []
#     save_zip_dir = os.getcwd()+"/downZip"
#     for project_url in trendingList:
#         saved_dir = downMainZip(project_url, save_zip_dir)
#         all_zip_dir.append(saved_dir)
#     print(f"\n[all downloaded zip dir]:{all_zip_dir}\n")

#     ''' [3]. 解压每个项目的zip '''
#     print("\n-----------------------[3]. 解压每个项目的zip----------------------------")
#     all_unzip_dir = []
#     unzip_dst_dir = os.getcwd()+"/unZip"
#     for zip_dir in all_zip_dir:
#         unzip_dir = unzipMainZip(zip_dir, unzip_dst_dir)
#         all_unzip_dir.append(unzip_dir)
#     print(f"\n[all unzipped project dir]:{all_unzip_dir}\n")

#     ''' [4]. 读取每个项目的readme文件内容 '''
#     print("\n------------------[4]. 读取每个项目的readme文件内容-----------------------")


class GitHubCrawler:
    def __init__(self, data_range, save_zip_dir=None, unzip_dst_dir=None):
        print(f"begin crawler GitHub! \n data_range: {data_range}")
        # https://github.com/trending?since=daily
        # https://github.com/trending?since=weekly
        # https://github.com/trending?since=monthly
        if (data_range not in ["daily", "weekly", "monthly"]):
            print(f'{data_range} not in ["daily", "weekly", "monthly"], use default "daily"')
            data_range = "daily"
        self.pageUrl = "https://github.com/trending?since=" + data_range

        self.trendingList = []
        self.all_zip_dir = []
        self.all_unzip_dir = []
        self.save_zip_dir = (
            save_zip_dir if save_zip_dir is not None else os.getcwd() + "/downZip"
        )
        self.unzip_dst_dir = (
            unzip_dst_dir if unzip_dst_dir is not None else os.getcwd() + "/downZip"
        )

    def getTrendingList(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        all_list = []
        repo_links = soup.find_all("h2", class_="h3 lh-condensed")
        for link in repo_links:
            repo_url = "https://github.com" + link.a["href"]
            all_list.append(repo_url)
        return all_list

    def find_zipball_url(self, json_data, key_word):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key == key_word:
                    return value
                else:
                    result = self.find_zipball_url(value, key_word)
                    if result is not None:
                        return result
        elif isinstance(json_data, list):
            for item in json_data:
                result = self.find_zipball_url(item, key_word)
                if result is not None:
                    return result

    def getMainZipUrl(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        repo_links = soup.find_all("script", type="application/json")
        for link in repo_links:
            json_data = json.loads(link.string)
            result = self.find_zipball_url(json_data, "zipballUrl")
            if result != None:
                return "https://github.com" + result
        return None

    def downMainZip(self, url, dst_dir):
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        zip_url = self.getMainZipUrl(url)
        print(f"[find zip url: {zip_url}]")
        response = requests.get(zip_url)
        match = re.search(r"\/([^\/]+)\/?$", url)
        if match:
            content = match.group(1)
            saved_dir = f"{dst_dir}/{content}.zip"
            with open(saved_dir, "wb") as f:
                f.write(response.content)
                print(f"downloaded: {content}.zip")
        return saved_dir

    def unzipMainZip(self, zip_dir, dst_dir):
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        with zipfile.ZipFile(zip_dir, "r") as zip_ref:
            zip_ref.extractall(dst_dir)
        content = re.search(r"\/([^\/]+)\.zip$", zip_dir).group(1)
        unzip_dir = f"{dst_dir}/{content}-main"
        print(f"[have unzipped: {unzip_dir}]")
        return unzip_dir

    def run(self, use_topN, save_zip_dir=None, unzip_dst_dir=None):
        '''
        # use_top(n for topN, 0 for all)
        '''
        if save_zip_dir is not None:
            self.save_zip_dir = save_zip_dir
        if unzip_dst_dir is not None:
            self.unzip_dst_dir = unzip_dst_dir

        print("\n--------------------[1]. trending页面所有项目网址链接--------------------")
        trendingList = crawler.getTrendingList(self.pageUrl)
        if(use_topN != 0):
            self.trendingList = trendingList[:use_topN]
        else:
            self.trendingList = trendingList[:]
        print(f"共有{len(self.trendingList)}个项目, 分别是：")
        list(map(lambda x: print(x), self.trendingList))

        print("\n------------------------[2]. 每个项目下载zip----------------------------")
        for project_url in self.trendingList:
            saved_dir = crawler.downMainZip(project_url, self.save_zip_dir)
            self.all_zip_dir.append(saved_dir)
        print(f"\n[all downloaded zip dir]:{self.all_zip_dir}\n")

        print("\n-----------------------[3]. 解压每个项目的zip----------------------------")
        for zip_dir in self.all_zip_dir:
            unzip_dir = crawler.unzipMainZip(zip_dir, self.unzip_dst_dir)
            self.all_unzip_dir.append(unzip_dir)
        print(f"\n[all unzipped project dir]:{self.all_unzip_dir}\n")

        print("\n------------------[4]. 读取每个项目的readme文件内容-----------------------")

# def get_one_readme_file(project_dir):
#     readme_file = next((file for file in os.listdir(project_dir) if file.lower() == 'readme.md'), None)
#     content = None
#     if readme_file is not None:
#         with open(os.path.join(project_dir, readme_file), 'r') as f:
#             content = f.read()
#     else:
#         print(f'{project_dir}:No readme file found.')
#     if(content != None):
#         print(f"[have readme file content: {os.path.join(project_dir, readme_file)}]")
#     else:
#         print(f"[read readme content filed: {os.path.join(project_dir, readme_file)}]")
#     return content

# def get_all_reafme_files(use_topN, all_unzip_dir):
#     '''
#     # use_top(n for topN, 0 for all)
#     '''
#     if(use_topN != 0):
#         all_unzip_dir = all_unzip_dir[:use_topN]
#     else:
#         all_unzip_dir = all_unzip_dir[:]
#     print(f"共有{len(all_unzip_dir)}个项目, 分别是：")
#     list(map(lambda x: print(x), all_unzip_dir))
#     for project_dir in all_unzip_dir:
#         content = get_one_readme_file(project_dir)
#         # print(content)
class ReadmeFileReader:
    def __init__(self, all_unzip_dir=None):
        print("init ReadmeFileReader")
        if not isinstance(all_unzip_dir, list):
            raise TypeError("all_unzip_dir should be a list")
        if(len(all_unzip_dir) == 0):
            raise ValueError("all_unzip_dir cannot be None")
        self.all_unzip_dir = (
            all_unzip_dir if all_unzip_dir is not None else os.getcwd() + "/downZip"
        )

    def get_one_readme_file(self, project_dir):
        readme_file = next((file for file in os.listdir(project_dir) if file.lower() == 'readme.md'), None)
        content = None
        if readme_file is not None:
            with open(os.path.join(project_dir, readme_file), 'r') as f:
                content = f.read()
        else:
            print(f'{project_dir}: No readme file found.')
        if content is not None:
            print(f"[have readme file content: {os.path.join(project_dir, readme_file)}]")
        else:
            print(f"[read readme content filed: {os.path.join(project_dir, readme_file)}]")
        return content

    def get_all_readme_files(self, use_topN):
        if use_topN != 0:
            self.all_unzip_dir = self.all_unzip_dir[:use_topN]
        else:
            self.all_unzip_dir = self.all_unzip_dir[:]
        print(f"共有{len(self.all_unzip_dir)}个项目, 分别是：")
        list(map(lambda x: print(x), self.all_unzip_dir))
        for project_dir in self.all_unzip_dir:
            content = self.get_one_readme_file(project_dir)
            # print(content)

if __name__ == "__main__":
    # trending top N
    use_topN = 2
    '''
    # download Github Trending("daily", "weekly", "monthly") projects zips & unzip.
    '''
    save_zip_dir = os.getcwd() + "/downZip"
    unzip_dst_dir = os.getcwd() + "/unZip"
    crawler = GitHubCrawler("daily", save_zip_dir, unzip_dst_dir) # "daily", "weekly", "monthly"
    crawler.run(use_topN) # use_topN(n for topN, 0 for all)
    # print(crawler.unzip_dst_dir)
    # print(crawler.all_unzip_dir)

    '''
    # read downloaded projects README.md files.
    '''
    # all_unzip_dir = crawler.all_unzip_dir
    # get_all_reafme_files(use_topN, all_unzip_dir)

    all_unzip_dir = crawler.all_unzip_dir
    reader = ReadmeFileReader(all_unzip_dir)
    reader.get_all_readme_files(use_topN) # use_topN(n for topN, 0 for all)
    




















