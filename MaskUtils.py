import cv2
import Constants
import numpy as np


def getMask(image, color_range):
    hsv_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
    mask = np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype='uint8')
    for min_range, max_range in color_range:
        mask += cv2.inRange(hsv_image, min_range, max_range)
    return mask


def getMatchRate(mask, fit_mask):
    correlation = mask * fit_mask
    area_correlation = np.count_nonzero(correlation)
    area_fit_mask = np.count_nonzero(fit_mask)
    return area_correlation / area_fit_mask, area_correlation
