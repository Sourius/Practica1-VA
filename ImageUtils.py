import os
import cv2
import Constants


def read(image_path):
    return cv2.imread(image_path, 1)


def readAndCrop(image_path, dims):
    return crop(cv2.imread(image_path, 1), dims)


def save(image, path):
    cv2.imwrite(path, image)


def crop(image, dims):
    return image[dims[0]:dims[1], dims[2]:dims[3]]


def resize(image):
    return cv2.resize(image, (Constants.DIM_X, Constants.DIM_Y))


def equalize(image):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(img_gray)


def drawRectangle(image, dims):
    upper_left = (dims[2]-2, dims[0]-2)  # x1, y1
    lower_right = (dims[3]+2, dims[1]+2)  # x2, y2
    return cv2.rectangle(image, upper_left, lower_right, (0, 0, 255), 4)


def load_paths(dir_path):
    paths = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            paths.append(os.path.join(root, f))
    return paths


def dir_to_type(folder):
    try:
        folder = int(folder)
        if folder == 14:  # es stop
            return 3
        elif folder in [x for x in range(18, 32)] + [11]:  # peligro
            return 2
        elif folder in [x for x in range(0, 11)] + [15, 16]:  # prohibicion
            return 1
    except ValueError:
        return None


def load_images(dir_path):
    image_type_map = {1: [], 2: [], 3: []}
    ficheros = os.listdir(dir_path)
    if "gt.txt" in ficheros:
        file_path = os.path.join(dir_path, "gt.txt")
        f = open(file_path, mode='r', encoding='utf-8')
        for line_gt in f:
            if line_gt != '\n':
                img_path, x1, y1, x2, y2, folder = line_gt.strip().split(";")
                img_type = dir_to_type(folder)
                if img_type is not None:
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    img = readAndCrop(os.path.join(dir_path, img_path), (y1, y2, x1, x2))
                    img = resize(img)
                    image_type_map[img_type].append(img)
        f.close()
    else:
        for root, _, files in os.walk(dir_path):
            folder = os.path.basename(root)
            img_type = dir_to_type(folder)
            if root != dir_path and img_type is not None:
                for file in files:
                    img = read(os.path.join(root, file))
                    img = resize(img)
                    image_type_map[img_type].append(img)
    return image_type_map
