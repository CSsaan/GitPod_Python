from PIL import Image
im = Image.open('zebra.png')
im = im.convert('RGB')
im.save('zebra.jpg') # , quality=55
