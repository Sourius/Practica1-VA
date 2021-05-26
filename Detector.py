import ImageUtils
import Constants
import cv2
import numpy as np
from MSERDetector import MSERDetector
import MaskUtils
import os
from ProgressBar import printProgressBar
import shutil


def area(region):
    y1, y2, x1, x2 = region
    return (y2 - y1) * (x2 - x1)


def esta_solapada(region_peq, region_grande):
    centro_peq = ((region_peq[0] + region_peq[1]) // 2, (region_peq[2] + region_peq[3]) // 2)
    return (region_grande[0] <= centro_peq[0] <= region_grande[1]) and (
            region_grande[2] <= centro_peq[1] <= region_grande[3])


def obtener_mejor_parecido(deteccion1, deteccion2):
    region_antigua, match_antiguo, _ = deteccion1
    region_nueva, match_nuevo, _ = deteccion2
    area_antigua = area(region_antigua)
    area_nueva = area(region_nueva)
    proporcion = area_nueva / area_antigua
    if proporcion > 1.5 or match_nuevo > match_antiguo:
        return deteccion1
    else:
        return deteccion2


def filter_regions(detecciones):
    filtered_regions = []
    while detecciones:
        deteccion1 = detecciones.pop()
        overlap_regions = []
        for deteccion2 in detecciones:
            if esta_solapada(deteccion1[0], deteccion2[0]) or esta_solapada(deteccion2[0], deteccion1[0]):
                overlap_regions.append(deteccion2)
        # obtener la mejor de todas
        mejor = deteccion1
        while overlap_regions:
            other = overlap_regions.pop()
            detecciones.remove(other)
            mejor = obtener_mejor_parecido(mejor, other)
        filtered_regions.append(mejor)
    return filtered_regions


class Detector:
    def __init__(self):
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, Constants.KERNEL_SIZE)
        self.avg_masks = {1: np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype=float),
                          2: np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype=float),
                          3: np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype=float)}
        self.mser = MSERDetector()
        self.color_ranges = [[np.array([160, 40, 10]), np.array([180, 255, 255])], [np.array([0, 40, 10]),
                                                                                    np.array([10, 255, 255])]]

    def train(self, image_type_map):
        for img_type in image_type_map.keys():
            for image in image_type_map.get(img_type):
                self.avg_masks[img_type] += MaskUtils.getMask(image, self.color_ranges)
            self.avg_masks[img_type] = self.avg_masks[img_type] / 255
            self.avg_masks[img_type] = np.array(self.avg_masks[img_type] > round(self.avg_masks[img_type].mean()),
                                                dtype=float)
            self.avg_masks[img_type] = cv2.morphologyEx(self.avg_masks[img_type], cv2.MORPH_OPEN, self.kernel,
                                                        iterations=1)

    def detect(self, image):
        interest_regions = self.mser.applyMser(ImageUtils.equalize(image))
        detecciones = []
        for region in interest_regions:
            img_cropped = ImageUtils.crop(image, region)
            img_resized = ImageUtils.resize(img_cropped)
            mask = MaskUtils.getMask(img_resized, self.color_ranges)

            match_rates_scores = np.array(
                [MaskUtils.getMatchRate(mask, avg_mask) for avg_mask in list(self.avg_masks.values())])
            match_rates = np.array([mrs[0] for mrs in match_rates_scores])
            scores = np.array([mrs[1] for mrs in match_rates_scores])
            pos = scores.argmax()
            match_rate = match_rates[pos]
            if match_rate >= Constants.MIN_MATCH_RATE:
                detecciones.append((region, match_rate, pos+1))
        return filter_regions(detecciones)

    def train_from_dir(self, train_dir):
        self.train(ImageUtils.load_images(train_dir))

    def detect_from_dir(self, test_dir):
        output_file = open(Constants.RESULTS_FILE, "w")
        output_type_file = open(Constants.RESULTS_TYPE_FILE, "w")
        if os.path.exists(Constants.RESULTS_DIR):
            shutil.rmtree(Constants.RESULTS_DIR)
            #os.rmdir(Constants.RESULTS_DIR)
        os.mkdir(Constants.RESULTS_DIR)
        img_paths = ImageUtils.load_paths(test_dir)
        i = 0
        total = len(img_paths)
        for img_path in img_paths:
            i += 1
            printProgressBar(i, total, prefix='Progreso:', suffix='completado', length=50)
            img = ImageUtils.read(img_path)
            img_rectangle = img.copy()
            img_name = os.path.basename(img_path)
            for detec in self.detect(img):
                # generar las salidas
                img_rectangle = ImageUtils.drawRectangle(img_rectangle, detec[0])
                # guardar detecciones
                # devolver resultado por tipo
                y1, y2, x1, x2 = detec[0]
                match_rate = detec[1]
                tipo = detec[2]
                output_line = img_name + ";" + str(x1) + ";" + str(y1) + ";" + str(x2) + ";" + str(y2) + ";" + str(
                    1) + ";" + str(round(match_rate * 100, 2)) + '\n'
                output_file.write(output_line)
                output_line = img_name + ";" + str(x1) + ";" + str(y1) + ";" + str(x2) + ";" + str(y2) + ";" + str(
                    tipo) + ";" + str(round(match_rate * 100, 2)) + '\n'
                output_type_file.write(output_line)
            image_save_dir = os.path.join(Constants.RESULTS_DIR, img_name)
            ImageUtils.save(img_rectangle, image_save_dir)
        output_file.close()
        output_type_file.close()
