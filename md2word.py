import pypandoc
'''
# 此命令时候ubuntu系统，其他系统自行更改
sudo apt install pandoc	
# 查看 pandoc的执行路径
which pandoc #一般在 /usr/bin/pandoc
# 将命令加入的应用中。我的项目是Django，因此我在需要用的应用的__init__.py加入代码
import  os
os.environ.setdefault('PYPANDOC_PANDOC', '/usr/bin/pandoc')
# 如果你发现还是不行，尝试在settings.py中也加入

'''
# 定义输入和输出文件的路径
input_file = '/workspace/GitPod_Python/output/docx_to_md.md'
output_file = '/workspace/GitPod_Python/output/example.docx'


# 调用pypandoc库进行转换
pypandoc.convert_file(input_file, 'docx', outputfile=output_file)