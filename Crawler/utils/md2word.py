import pypandoc
'''
# 此命令时候ubuntu系统，其他系统自行更改
sudo apt-get update
sudo apt install pandoc	
# 查看 pandoc 的执行路径
which pandoc #一般在 /usr/bin/pandoc
# 将命令加入的应用中。我的项目是Django，因此我在需要用的应用的__init__.py加入代码
import  os
os.environ.setdefault('PYPANDOC_PANDOC', '/usr/bin/pandoc')
# 如果你发现还是不行，尝试在settings.py中也加入
'''
# 定义输入和输出文件的路径
filename = "VideoMatting"
input_file = f'./src/{filename}.md'
output_file = f'./dst/{filename}.docx'


# 调用pypandoc库进行转换
pypandoc.convert_file(input_file, 'docx', outputfile=output_file)
print(f'saved {input_file} to {output_file}')