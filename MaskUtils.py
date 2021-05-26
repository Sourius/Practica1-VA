import cv2
import Constants
import numpy as np

# devuelve la mascara de rojo de una imagen
# recibe la imagen y color_range, rango de valores de rojo en hsv
# los valores de rojo en hsv se utilizan para generar las mascaras
def getMask(image, color_range):
    hsv_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
    mask = np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype='uint8')
    for min_range, max_range in color_range:
        mask += cv2.inRange(hsv_image, min_range, max_range)
    return mask

# devuelve la tasa de parecido entre dos mascaras
# recibe mask la mascara de la imagen y fitmask la mascara media 
def getMatchRate(mask, fit_mask):
    correlation = mask * fit_mask
    area_correlation = np.count_nonzero(correlation)
    area_fit_mask = np.count_nonzero(fit_mask)
    return area_correlation / area_fit_mask, area_correlation
