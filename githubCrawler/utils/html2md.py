# 导入markdownify模块
import markdownify
from bs4 import BeautifulSoup

# 定义输入和输出文件的路径
filename = "1111"
input_file = f'./src/{filename}.html'
output_file = f'./dst/{filename}.md'

# 读取HTML文件
with open(input_file, "r", encoding="utf-8") as file:
   html_content = file.read()
# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, "html.parser")
# 获取HTML文本
html_text = soup.get_text()

# 使用markdownify()函数将HTML转换为Markdown
markdown_text = markdownify.markdownify(html_text)

# 显示转换后的Markdown文本
print(markdown_text)

# 将转换后的Markdown文本保存为.md文件
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(markdown_text)

print(f"Markdown file {output_file} has been created.")