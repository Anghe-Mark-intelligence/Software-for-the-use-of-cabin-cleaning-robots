from PIL import Image

# 打开jpg文件
img = Image.open(r"D:\anaconda\robotsystemheang\softwarelogo.jpg")

# 将图片转换为ico文件，并保存
img.save(r"D:\anaconda\robotsystemheang\softwarelogo.ico", format="ICO", sizes=[(64, 64), (32, 32), (16, 16)])
