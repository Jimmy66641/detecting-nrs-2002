# -*- coding=utf-8 -*-
import glob
import platform
import time
from PIL import Image
from skimage.feature import hog
import numpy as np
import os
import joblib
from sklearn.svm import LinearSVC
import shutil
import sys
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn import metrics


label_map = {0: '0',
             1: '1'
             }
# 训练集图片的位置
train_image_path = '/root/Downloads/Asvmadd300/train_nrs'
# 测试集图片的位置
test_image_path = '/root/Downloads/Asvmadd300/test_nrs'

# 训练集标签的位置
train_label_path = os.path.join('/root/Downloads/Asvmadd300/train_nrs/','mapnrs_train.txt')
 # 测试集标签的位置
test_label_path = os.path.join('/root/Downloads/Asvmadd300/test_nrs/','mapnrs_test.txt')

image_height = 300
image_width = 300

train_feat_path = '/root/Downloads/trainfinal_feat/'
test_feat_path = '/root/Downloads/testfinal_feat'
model_path = '/root/Downloads/modeladd'


# 获得图片列表
def get_image_list(filePath, nameList):
    print('read image from ',filePath)
    img_list = []
    for name in nameList:
        temp = Image.open(os.path.join(filePath,name))
        img_list.append(temp.copy())
        temp.close()
    return img_list


# 提取特征并保存
def get_feat(image_list, name_list, label_list, savePath):
    i = 0
    for image in image_list:
        try:
            # 如果是灰度图片 ，把3改为-1
            image = np.reshape(image, (image_height, image_width, 3))
        except:
            print('发送了异常，图片大小size不满足要求：',name_list[i])
            continue
        gray = rgb2gray(image) / 255.0
        # ???????????
        fd = hog(gray, orientations=9, block_norm='L1', pixels_per_cell=[6,6], cells_per_block=[2,2], visualize=False)
        fd = np.concatenate((fd, [label_list[i]]))
        fd_name = name_list[i] + '.feat'
        fd_path = os.path.join(savePath, fd_name)
        joblib.dump(fd, fd_path)
        i += 1
    print("Test features are extracted and saved.")


# 变成灰度图片
def rgb2gray(im):
    gray = im[:, :, 0] * 0.2989 + im[:, :, 1] * 0.5870 + im[:, :, 2] * 0.1140
    return gray


# 获得图片名称与对应的类别
def get_name_label(file_path):
    print("read label from ",file_path)
    name_list = []
    label_list = []
    with open(file_path) as f:
        for line in f.readlines():
            #一般是name label  三部分，所以至少长度为3  所以可以通过这个忽略空白行
            if len(line)>=3:
                name_list.append(line.split(' ')[0])
                label_list.append(line.split(' ')[1].replace('\n','').replace('\r',''))
                if not str(label_list[-1]).isdigit():
                    print("label必须为数字，得到的是",label_list[-1],"程序终止，请检查文件")
                    exit(1)
    return name_list, label_list


# 提取特征
def extra_feat():
    train_name, train_label = get_name_label(train_label_path)
    test_name, test_label = get_name_label(test_label_path)

    train_image = get_image_list(train_image_path, train_name)
    test_image = get_image_list(test_image_path, test_name)
    get_feat(train_image, train_name, train_label, train_feat_path)
    get_feat(test_image, test_name, test_label, test_feat_path)


# 创建存放特征的文件夹
def mkdir():
    if not os.path.exists(train_feat_path):
        os.mkdir(train_feat_path)
    if not os.path.exists(test_feat_path):
        os.mkdir(test_feat_path)



# 训练和测试
def train_and_test():
    t0 = time.time()
    features = []
    labels = []
    correct_number = 0
    total = 0
    for feat_path in glob.glob(os.path.join(train_feat_path, '*.feat')):
        data = joblib.load(feat_path)
        features.append(data[:-1])
        labels.append(data[-1])
    print("Training a SVM Classifier.")


    #clf = LinearSVC()
    # ?? GridSearchCV ????
    """estimator_SVM = SVC(gamma='scale')
    parameters_SVM = {
        'C': (0.1, 15.0, 0.1),
        'kernel': ('linear', 'poly', 'rbf'),
        'coef0': (0.0, 10.0, 1.0),
        'shrinking': (True, False),

    }  # with GridSearch
    grid_search_SVM = GridSearchCV (
    estimator = estimator_SVM,
    param_grid = parameters_SVM,
    scoring = 'accuracy',
    n_jobs = - 1,
    cv = 5)"""
    """param_grid = {'C': [10, 20, 30],
                  'gamma': [1e5],
                  'kernel': ['rbf']}
    grid = GridSearchCV(SVC(), param_grid, refit=True, verbose=3)
    # fitting the model for grid search
    grid.fit(features, labels)"""

    grid = SVC(C=100, kernel='rbf',gamma=0.0001)
    scalar=StandardScaler()
    pca=PCA(n_components=80)
    features=scalar.fit_transform(features)
    features=pca.fit_transform(features)
    grid.fit(features, labels)

    # 下面的代码是保存模型的
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    joblib.dump(grid, model_path + 'model')
    # 下面的代码是加载模型  可以注释上面的代码   直接进行加载模型  不进行训练
    # clf = joblib.load(model_path+'model')
    print("??????????model????")
    # exit()

    result_list = []
    for feat_path in glob.glob(os.path.join(test_feat_path, '*.feat')):
        total += 1
        if platform.system() == 'Windows':
            symbol = '\\'
        else:
            symbol = '/'
        #image_name = feat_path.split(symbol)[1].split('.feat')[0]
        image_name = feat_path.split('.')[0]
        data_test = joblib.load(feat_path)
        data_test_feat = data_test[:-1].reshape((1, -1)).astype(np.float64)
        result = grid.predict(data_test_feat)
        result_list.append(image_name + ' ' + label_map[int(result[0])] + '\n')
        if int(result[0]) == int(data_test[-1]):
            correct_number += 1
    write_to_txt(result_list)
    rate = float(correct_number) / total
    t1 = time.time()

    print('accuracy %f' % rate)
    print('time : %f' % (t1 - t0))
    # Parameter setting that gave the best results on the hold out data.

def write_to_txt(list):
    with open('result.txt', 'w') as f:
        f.writelines(list)
    print('每张图片的识别结果存放在result.txt里面')


if __name__ == '__main__':

    mkdir()  
    if sys.version_info < (3,):
        need_extra_feat = input('是否需要重新获取特征？y/n\n')
    else:
        need_extra_feat = input('是否需要重新获取特征？y/n\n')

    if need_extra_feat == 'y':
        shutil.rmtree(train_feat_path)
        shutil.rmtree(test_feat_path)
        mkdir()
        extra_feat()  

    train_and_test() 
