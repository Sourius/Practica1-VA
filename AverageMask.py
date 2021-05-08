from MaskMaker import MaskMaker
from TSType import TSType
import numpy as np
import cv2


class AverageMask:
    def __init__(self, kernel, ts_type, dim_x, dim_y):
        self.ts_type = ts_type
        self.kernel = kernel
        self.maskMaker = MaskMaker(kernel, dim_x, dim_y)
        self.value = np.zeros((dim_x, dim_y), dtype=bool)
        self.avg_mask_or = np.zeros((dim_x, dim_y), dtype=bool)

    def getType(self):
        return self.ts_type

    def getValue(self):
        return self.value

    def add_learning_image(self, cropped_image):
        red_mask = self.maskMaker.getMask(cropped_image)
        self.avg_mask_or = self.avg_mask_or + red_mask

    # generar mascara media
    def generateAVGMask(self):
        aux = self.avg_mask_or / 255
        aux = np.array(aux > round(aux.mean()), dtype=float)
        self.value = cv2.morphologyEx(aux, cv2.MORPH_OPEN, self.kernel, iterations=1)
