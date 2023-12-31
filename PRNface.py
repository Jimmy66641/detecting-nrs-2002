import cv2
import numpy as np
import math
from collections import defaultdict
from PIL import Image,ImageDraw
from matplotlib.pyplot import imshow
import matplotlib.pyplot as plt
import face_recognition  # install from https://github.com/ageitgey/face_recognition

#人脸关键点可视化函数
def visualize_landmark(image_array, landmarks):
    """ plot landmarks on image
    :param image_array: numpy array of a single image
    :param landmarks: dict of landmarks for facial parts as keys and tuple of coordinates as values
    :return: plots of images with landmarks on
    """
    origin_img = Image.fromarray(image_array)
    draw = ImageDraw.Draw(origin_img)
    for facial_feature in landmarks.keys():
        draw.point(landmarks[facial_feature])
    imshow(origin_img)

def align_face(image_array, landmarks):
    """ align faces according to eyes position
    :param image_array: numpy array of a single image
    :param landmarks: dict of landmarks for facial parts as keys and tuple of coordinates as values
    :return:
    rotated_img:  numpy array of aligned image
    eye_center: tuple of coordinates for eye center
    angle: degrees of rotation
    """
    # get list landmarks of left and right eye
    left_eye = landmarks['left_eye']
    right_eye = landmarks['right_eye']
    # calculate the mean point of landmarks of left and right eye
    left_eye_center = np.mean(left_eye, axis=0).astype("int")
    right_eye_center = np.mean(right_eye, axis=0).astype("int")
    # compute the angle between the eye centroids
    dy = right_eye_center[1] - left_eye_center[1]
    dx = right_eye_center[0] - left_eye_center[0]
    # compute angle between the line of 2 centeroids and the horizontal line
    angle = math.atan2(dy, dx) * 180. / math.pi
    # calculate the center of 2 eyes
    eye_center = (int((left_eye_center[0] + right_eye_center[0]) // 2),
                  int((left_eye_center[1] + right_eye_center[1]) // 2))
    # at the eye_center, rotate the image by the angle
    rotate_matrix = cv2.getRotationMatrix2D(eye_center, angle, scale=1)
    rotated_img = cv2.warpAffine(image_array, rotate_matrix, (image_array.shape[1], image_array.shape[0]))
    return rotated_img, eye_center, angle


def rotate(origin, point, angle, row):
    """ rotate coordinates in image coordinate system
    :param origin: tuple of coordinates,the rotation center
    :param point: tuple of coordinates, points to rotate
    :param angle: degrees of rotation
    :param row: row size of the image
    :return: rotated coordinates of point
    """
    x1, y1 = point
    x2, y2 = origin
    y1 = row - y1
    y2 = row - y2
    angle = math.radians(angle)
    x = x2 + math.cos(angle) * (x1 - x2) - math.sin(angle) * (y1 - y2)
    y = y2 + math.sin(angle) * (x1 - x2) + math.cos(angle) * (y1 - y2)
    y = row - y
    return int(x), int(y)

def rotate_landmarks(landmarks, eye_center, angle, row):
    """ rotate landmarks to fit the aligned face
    :param landmarks: dict of landmarks for facial parts as keys and tuple of coordinates as values
    :param eye_center: tuple of coordinates for eye center
    :param angle: degrees of rotation
    :param row: row size of the image
    :return: rotated_landmarks with the same structure with landmarks, but different values
    """
    rotated_landmarks = defaultdict(list)
    for facial_feature in landmarks.keys():
        for landmark in landmarks[facial_feature]:
            rotated_landmark = rotate(origin=eye_center, point=landmark, angle=angle, row=row)
            rotated_landmarks[facial_feature].append(rotated_landmark)
    return rotated_landmarks


def corp_face(image_array, landmarks):
    """ crop face according to eye,mouth and chin position
    :param image_array: numpy array of a single image
    :param landmarks: dict of landmarks for facial parts as keys and tuple of coordinates as values
    :return:
    cropped_img: numpy array of cropped image
    """

    eye_landmark = np.concatenate([np.array(landmarks['left_eye']),
                                   np.array(landmarks['right_eye'])])
    eye_center = np.mean(eye_landmark, axis=0).astype("int")
    lip_landmark = np.concatenate([np.array(landmarks['top_lip']),
                                   np.array(landmarks['bottom_lip'])])
    lip_center = np.mean(lip_landmark, axis=0).astype("int")
    mid_part = lip_center[1] - eye_center[1]
    top = eye_center[1] - mid_part * 30 / 35
    bottom = lip_center[1] + mid_part

    w = h = bottom - top
    x_min = np.min(landmarks['chin'], axis=0)[0]
    x_max = np.max(landmarks['chin'], axis=0)[0]
    x_center = (x_max - x_min) / 2 + x_min
    left, right = (x_center - w / 2, x_center + w / 2)

    pil_img = Image.fromarray(image_array)
    left, top, right, bottom = [int(i) for i in [left, top, right, bottom]]
    cropped_img = pil_img.crop((left, top, right, bottom))
    cropped_img = np.array(cropped_img)
    return cropped_img, left, top

def transfer_landmark(landmarks, left, top):
    """transfer landmarks to fit the cropped face
    :param landmarks: dict of landmarks for facial parts as keys and tuple of coordinates as values
    :param left: left coordinates of cropping
    :param top: top coordinates of cropping
    :return: transferred_landmarks with the same structure with landmarks, but different values
    """
    transferred_landmarks = defaultdict(list)
    for facial_feature in landmarks.keys():
        for landmark in landmarks[facial_feature]:
            transferred_landmark = (landmark[0] - left, landmark[1] - top)
            transferred_landmarks[facial_feature].append(transferred_landmark)
    return transferred_landmarks

#40，42，57，62，74，77，80，81，83，94，95，102，110，111，119,159,191,201,204,214,221,226,228,230,233,262没检测出脸
#283,303,329,353,360,375,385,404,425,440,443,450,458,462,466,497,526,527,560,573,583,591,594,596,604,606
#623,682,693,729,746,788,790,800,801,802,810,820,823,830,831,837,851,854,859,873,879,880,895,920,946
if __name__ == "__main__":
    i=181
    faces_path = "/Users/apple/Apicture/"+str(i)+".jpg"
    #faces_path = "/Users/apple/Downloads/humanface.jpg"

    image = cv2.imread(faces_path)
    #img_bgr = cv2.imread(faces_path)
    """
    b,g,r = cv2.split(image)          #分别提取B、G、R通道
    image = cv2.merge([r,g,b])
    """
    Image.fromarray(image)
    face_landmarks_list = face_recognition.face_landmarks(image, model="large")
    if (len(face_landmarks_list) == 0):
        print(i,",")
        #continue
    face_landmarks_dict = face_landmarks_list[0]
    #print(face_landmarks_dict, end=" ")
    #visualize_landmark(image_array=image,landmarks=face_landmarks_dict)
    #plt.title('original_keypoint')
    #plt.show()

    aligned_face, eye_center, angle = align_face(image_array=image, landmarks=face_landmarks_dict)
    #stack_img=Image.fromarray(np.hstack((image,aligned_face)))
    visualize_landmark(image_array=aligned_face,landmarks=face_landmarks_dict)
    cv2.imwrite("/Users/apple/Downloads/humanfacealigned.jpg", aligned_face)
    plt.imshow(aligned_face)
    plt.title('rotate_image')
    plt.show()

    rotated_landmarks = rotate_landmarks(landmarks=face_landmarks_dict, eye_center=eye_center, angle=angle, row=image.shape[0])
    #visualize_landmark(image_array=aligned_face,landmarks=rotated_landmarks)
    #plt.title('rotate_keypoint')
    #plt.show()

    cropped_face, left, top = corp_face(image_array=aligned_face, landmarks=rotated_landmarks)
    #cropped_face=Image.fromarray(cropped_face)
    transferred_landmarks = transfer_landmark(landmarks=rotated_landmarks, left=left, top=top)
    visualize_landmark(image_array=cropped_face,landmarks=transferred_landmarks)
    #plt.title('cropped_face')
    #plt.show()
    #cropped_face=Image.fromarray(cropped_face)
    
    #resize要求img
    #cropped_resize=cropped_face.resize((100,100))
    cv2.imwrite("/Users/apple/Downloads/humanfaceacropped.jpg", cropped_face)
    plt.imshow(cropped_face)
    plt.title('cropped_resize')
    plt.show()
    
    #cv2要求numpy数组
    #cropped_resize=np.array(cropped_resize)

    face_locations = face_recognition.face_locations(aligned_face)
    for face_location in face_locations:
        top, right, bottom, left = face_location
        face_image = aligned_face[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        resized_face=pil_image.resize((100,100))
        resized_face=np.array(resized_face)
        #cv2.imwrite("/Users/apple/ApictureThen/new"+str(i)+".jpg",resized_face)
        cv2.imshow("xx", resized_face)
