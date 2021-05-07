import cv2
import numpy as np
from colorsys import hsv_to_rgb
from random import random


class MSERDetector:
    def __init__(self, delta, variation, area):
        self.setMSER(delta, variation, area)

    def setMSER(self, delta, variation, area):
        self.mser = cv2.MSER_create(_delta=delta, _max_variation=variation, _max_area=area)

    # APLICAR MSER
    def __detectRegions(self, img):
        interest_regions = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        return self.mser.detectRegions(img)

        # RECORTAR

    def __cropRegion(self, polygon, img):
        x, y, w, h = cv2.boundingRect(polygon)
        ratio_margin = 0.1  #  margen de proporcion
        ratio = h / w  # proporcion
        crop_margin_p100_range = (5, 21)  # % del margen del recorte de la zona de interes

        for i in range(crop_margin_p100_range[0], crop_margin_p100_range[1], 5):
            crop_margin_p100 = i
            crop_margin_x = w * crop_margin_p100 // 100  # margen lateral
            crop_margin_y = h * crop_margin_p100 // 100  # margen superior/interior

            # filtrar regiones
            if 1 - ratio_margin < ratio < 1 + ratio_margin:
                # recortar
                y1 = y - crop_margin_y
                y2 = y + h + crop_margin_y
                x1 = x - crop_margin_x
                x2 = x + w + crop_margin_x

                if (y1 < 0) or (x1 < 0) or (y2 > img.shape[0]) or (
                        x2 > img.shape[1]):  # deshacer margenes porque no caben
                    y1 = y
                    y2 = y + h
                    x1 = x
                    x2 = x + w
                return (y1, y2, x1, x2)

    def __getRandomColor(self):
        colorRGB = hsv_to_rgb(random(), 1, 1)
        return tuple(int(color * 255) for color in colorRGB)

    # APLICAR MSER, FILTRAR REGIONES, RECORTAR: teoria VA
    def applyMser(self, img):
        img_regions = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        interest_regions = []
        polygons = self.__detectRegions(img);
        for polygon in polygons[0]:
            region_cropped = self.__cropRegion(polygon, img)
            if (region_cropped is not None):
                interest_regions.append(region_cropped)
            img_regions = cv2.fillPoly(img_regions, [polygon], self.__getRandomColor())
        return img_regions, interest_regions
