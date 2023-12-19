import mammoth
from markdownify import markdownify
import time 
import os

# 转存 Word 文档内的图片
def convert_img(image):
    with image.open() as image_bytes:
        file_suffix = image.content_type.split("/")[1]
        path_file = os.path.join("./img", "{}.{}".format(str(time.time()), file_suffix))
        with open(path_file, 'wb') as f:
            f.write(image_bytes.read())
    return {"src": path_file}

if __name__ == "__main__":
    try:
    # 读取 Word 文件
        input_file_path = "/workspace/GitPod_Python/srcfile/LinuxC与C++开发实践.docx"
        with open(input_file_path, "rb") as docx_file:
            # 转化 Word 文档为 HTML
            result = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.img_element(convert_img))
            # 获取 HTML 内容
            html = result.value
            # 转化 HTML 为 Markdown
            md = markdownify(html, heading_style="ATX")
            print(md)
            output_html_path = "./output/docx_to_html.html"
            output_md_path = "./output/docx_to_md.md"
            with open(output_html_path, 'w', encoding='utf-8') as html_file, open(output_md_path, "w", encoding='utf-8') as md_file:
                html_file.write(html)
                md_file.write(md)
            messages = result.messages
    except Exception as e:
        print("Error occurred:", e)