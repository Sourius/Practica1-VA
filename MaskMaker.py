import numpy as np
import cv2


class MaskMaker:
    def __init__(self, kernel, dim_x, dim_y):
        self.kernel = kernel;
        self.dim_x = dim_x;
        self.dim_y = dim_y;
        self.ranges = [];
        self.__setRedColor();

    # inicializar rango de colores a rojo
    def __setRedColor(self):
        # posibles valores de los rojo
        # H 0 a 10 y 160 a 180 en openCV
        # S >= 40
        # V >= 30
        self.addHSVRange(np.array([0, 25, 0]), np.array([10, 125, 50]));
        self.addHSVRange(np.array([150, 50, 30]), np.array([180, 255, 255]));
        self.addHSVRange(np.array([0, 70, 30]), np.array([10, 255, 255]));

    def addHSVRange(self, low_range, high_range):
        self.ranges.append((low_range, high_range));

    def getMask(self, image):
        hsv_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV);
        mask = np.zeros((self.dim_x, self.dim_y));
        for min_range, max_range in self.ranges:
            mask += cv2.inRange(hsv_image, min_range, max_range);
        return mask;


