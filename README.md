# detecting-nrs-2002
u-net分割，参考：https://blog.csdn.net/ECHOSON/article/details/122914826

人脸68个关键点检测：https://github.com/ageitgey/face_recognition

svm代码貌似参考：https://github.com/rw1995/HOG_SVM/blob/master/hog_svm.py



提供的代码定义了一个名为的 Python 函数get_image_list，该函数采用两个参数：filePath和nameList。让我们分解该函数并了解它的作用：

def get_image_list(filePath, nameList):get_image_list：这一行定义了以两个输入参数filePath和命名的函数nameList。

print('read image from ',filePath)：该行打印一条消息，指示该函数正在从指定的位置读取图像filePath。

img_list = []：此行初始化一个名为 的空列表img_list，它将用于存储从文件中读取的图像。

for name in nameList:：此行启动一个循环，迭代nameList. 假定nameList为文件名（字符串）列表。

temp = Image.open(os.path.join(filePath,name))Image.open()：此行尝试使用Python 图像库 (PIL) 中的函数打开图像文件。它使用和os.path.join()的方法来组合形成完整的文件路径。filePathname

img_list.append(temp.copy())：如果图像文件成功打开，图像的副本将附加到列表中img_list。用于temp.copy()确保稍后关闭原始图像文件而不影响 中的图像img_list。

temp.close()：复制图像后，temp关闭临时图像对象以释放资源。

return img_list：读取所有图像并将其附加到 后img_list，该函数返回包含图像的列表。

nameList因此，该函数的目的是从指定的目录中读取指定的图像文件列表，filePath并将它们存储在名为 的列表中img_list。然后该函数返回图像列表作为输出
