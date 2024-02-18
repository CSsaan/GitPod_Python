import requests
from bs4 import BeautifulSoup
import re
import json
import os
import zipfile	
import gradio as gr
import argparse

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
    """
    GitHubCrawler类用于爬取GitHub上的趋势项目，并下载和解压项目的zip文件。

    初始化参数：
    - data_range: 数据范围，可选值为"daily", "weekly", "monthly"。
    - save_zip_dir: 下载zip文件的保存目录，默认为当前工作目录下的/downZip目录。
    - unzip_dst_dir: 解压zip文件的目标目录，默认为当前工作目录下的/downZip目录。

    方法：
    - getTrendingList: 获取GitHub趋势项目的链接列表。
    - find_zipball_url: 在JSON数据中查找zip文件的下载链接。
    - getMainZipUrl: 获取项目的main分支zip文件下载链接。
    - downMainZip: 下载项目的main分支zip文件。
    - unzipMainZip: 解压项目的zip文件。
    - run: 运行爬虫，下载和解压项目的zip文件。

    使用示例：
    - crawler = GitHubCrawler(data_range, save_zip_dir, unzip_dst_dir)
    - crawler.run(use_topN, save_zip_dir, unzip_dst_dir)
    """
    def __init__(self, data_range, save_zip_dir=None, unzip_dst_dir=None):
        print(f"begin crawler GitHub! \n data_range: {data_range}")
        # https://github.com/trending?since=daily
        # https://github.com/trending?since=weekly
        # https://github.com/trending?since=monthly
        if (data_range not in ["daily", "weekly", "monthly"]):
            print(f'{data_range} not in ["daily", "weekly", "monthly"], use default "daily"')
            data_range = "daily"
        self.pageUrl = "https://github.com/trending?since=" + data_range
        self.all_names = []
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
            self.all_names.append(content)
            saved_dir = f"{dst_dir}/{content}.zip"
            with open(saved_dir, "wb") as f:
                f.write(response.content)
                print(f"downloaded: {content}.zip")
        branch_name = re.search(r'([^/]+)\.zip$', zip_url).group(1)
        print("branch_name:", branch_name)
        return saved_dir, branch_name

    def unzipMainZip(self, zip_dir, main_or_master, dst_dir):
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        with zipfile.ZipFile(zip_dir, "r") as zip_ref:
            zip_ref.extractall(dst_dir)
        content = re.search(r"\/([^\/]+)\.zip$", zip_dir).group(1)
        unzip_dir = f"{dst_dir}/{content}-{main_or_master}"
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
        trendingList = self.getTrendingList(self.pageUrl)
        if(use_topN != 0):
            self.trendingList = trendingList[:use_topN]
        else:
            self.trendingList = trendingList[:]
        print(f"共有{len(self.trendingList)}个项目, 分别是：")
        list(map(lambda x: print(x), self.trendingList))

        print("\n------------------------[2]. 每个项目下载zip----------------------------")
        for project_url in self.trendingList:
            saved_dir, branch_name = self.downMainZip(project_url, self.save_zip_dir)
            self.all_zip_dir.append([saved_dir, branch_name])
        print(f"\n[all downloaded zip dir]:{self.all_zip_dir}\n")

        print("\n-----------------------[3]. 解压每个项目的zip----------------------------")
        for zip_dir, main_or_master in self.all_zip_dir:
            unzip_dir = self.unzipMainZip(zip_dir, main_or_master, self.unzip_dst_dir)
            self.all_unzip_dir.append(unzip_dir)
        print(f"\n[all unzipped project dir]:{self.all_unzip_dir}\n")

        


class ReadmeFileReader:
    """
    ReadmeFileReader类用于读取指定目录中的readme文件内容。

    初始化参数：
    - all_unzip_dir: 一个包含项目目录的列表，默认为None。如果未提供该参数，将使用当前工作目录下的/downZip目录。

    方法：
    - get_one_readme_file: 读取指定项目目录中的readme文件内容。
    - get_all_readme_files: 读取所有项目目录中的readme文件内容。

    使用示例：
    - reader = ReadmeFileReader(all_unzip_dir)
    - reader.get_all_readme_files(use_topN)
    """
    def __init__(self, all_unzip_dir=None):
        print("init ReadmeFileReader")
        self.all_name = []
        self.all_content = []
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
            with open(os.path.join(project_dir, readme_file), 'r', encoding='utf-8') as f:
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
            project_name = re.search(r"/([^/]+)$", project_dir).group(1)
            self.all_name.append(project_name)
            content = self.get_one_readme_file(project_dir)
            self.all_content.append(content)
            # print(content)

    def save_one_content(self, project_name, content, save_dir=None):
        save_dir = (
            save_dir if save_dir is not None else os.getcwd() + "/savedReadme"
        )
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # for project_dir in self.all_unzip_dir:
            # project_name = re.search(r"\/([^\/]+)\.zip$", zip_dir).group(1)
        with open(f'{save_dir}/{project_name}.md', 'w', encoding='utf-8') as f:
            f.write(content)
            print(f'[have saved readme.md: {save_dir}/{project_name}.md]')

    def save_all_content(self):
        if(len(self.all_name) == 0 or len(self.all_content) == 0):
            print("读取readme内容为空")
            raise ValueError("self.all_name or self.all_content is None")
        for i in range(len(self.all_name)):
            self.save_one_content(self.all_name[i], self.all_content[i], None)

# all_unzip_dir = []
# def run_crawler(data_range, use_topN, save_zip_dir, unzip_dst_dir):
#     # save_zip_dir = os.getcwd() + "/downZip"
#     # unzip_dst_dir = os.getcwd() + "/unZip"
#     crawler = GitHubCrawler(data_range, save_zip_dir, unzip_dst_dir)
#     crawler.run(use_topN)
#     all_unzip_dir = crawler.all_unzip_dir
#     # return all_unzip_dir

# def read_readme_files(all_unzip_dir, use_topN):
#     reader = ReadmeFileReader(all_unzip_dir)
#     reader.get_all_readme_files(use_topN)
#     return "Readme files read successfully."

if __name__ == "__main__":
    # args
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--use_topN', type=int, default=0, help='load github trending top N (0 for all)')
    parser.add_argument('--save_zip_dir', type=str, default="/downZip", help='save zip files dir')
    parser.add_argument('--unzip_dst_dir', type=str, default="/unZip", help='save unzip files dir')
    parser.add_argument('--data_range', type=str, default="daily", help=' "daily", "weekly", "monthly" ')
    args = parser.parse_args()

    '''
    # [1]、[2]、[3] download Github Trending("daily", "weekly", "monthly") projects zips & unzip.
    '''
    save_zip_dir = os.getcwd() + args.save_zip_dir
    unzip_dst_dir = os.getcwd() + args.unzip_dst_dir
    crawler = GitHubCrawler(args.data_range, save_zip_dir, unzip_dst_dir)
    crawler.run(args.use_topN)

    '''
    # [4]. read downloaded projects README.md files.
    '''
    print("\n------------------[4]. 读取每个项目的readme文件内容-----------------------")
    all_unzip_dir = crawler.all_unzip_dir
    reader = ReadmeFileReader(all_unzip_dir)
    reader.get_all_readme_files(args.use_topN) # use_topN(n for topN, 0 for all)
    # reader.all_content

    '''
    # TODO [5]. pass README.md content to AI Model(ChatGLM3\ChatGPT3.5...) -> 25 in 1
    '''
    print("\n-------------[5]. AI Model(ChatGLM3\ChatGPT3.5...)-----------------------")
    print("TODO···")
    '''
    # TODO [6]. new README.md or HTML (local picture)
    '''
    print("\n-----------------[6]. 保存每个readme文件AI输出内容------------------------")
    # reader.save_one_content(reader.all_name[0], reader.all_content[0], None)
    reader.save_all_content()
    '''
    # TODO [7]. upload to wechat or blog
    '''



    # if(False):
    #     save_zip_dir = os.getcwd() + "/downZip"
    #     unzip_dst_dir = os.getcwd() + "/unZip"
    #     with gr.Blocks() as demo:
    #         gr.HTML("""<h1 align="center">Github Crawler with ChatGLM3 Demo</h1>""")
    #         chatbot = gr.Chatbot()
    #         with gr.Row():
    #             with gr.Column(scale=4):
    #                 # with gr.Column(scale=4):
    #                 #     save_zip_dir = gr.File(label="Select Save Zip Folder", type='filepath', show_label=False, container=False)
    #                 #     unzip_dst_dir = gr.File(label="Select Unzip Folder", type='filepath', show_label=False, container=False)
    #                 with gr.Column(min_width=16, scale=1):
    #                     submitBtn = gr.Button("Run Crawler")
    #             with gr.Column(scale=2):
    #                 emptyBtn = gr.Button("Read README Files")
    #                 use_topN = gr.Slider(0, 25, value=1, step=1.0, label="Use Trending topN", interactive=True)
    #                 # top_p = gr.Slider(0, 1, value=0.8, step=0.01, label="Top P", interactive=True)
    #                 # temperature = gr.Slider(0.01, 1, value=0.6, step=0.01, label="Temperature", interactive=True)
    #         emptyBtn.click(lambda _: run_crawler("daily", use_topN, save_zip_dir, unzip_dst_dir))
    #         emptyBtn.click(lambda _: read_readme_files(all_unzip_dir, use_topN))
    #         # emptyBtn.click(lambda: None, None, chatbot, queue=False)
    #     demo.queue()
    #     demo.launch(server_name="127.0.0.1", server_port=8501, inbrowser=True, share=False)

















