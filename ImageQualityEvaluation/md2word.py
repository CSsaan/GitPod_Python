import pypandoc
# 定义输入和输出文件的路径
filename = "README"
input_file = f'/workspace/GitPod_Python/ImageQualityEvaluation/{filename}.md'
output_file = f'/workspace/GitPod_Python/ImageQualityEvaluation/{filename}.docx'
# 调用pypandoc库进行转换
pypandoc.convert_file(input_file, 'docx', outputfile=output_file)
print(f'saved {input_file} to {output_file}')

# pandoc -s README.md -o README.docx --extract-media=.