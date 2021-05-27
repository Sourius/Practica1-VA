import ImageUtils
import Constants
import cv2
import numpy as np
from MSERDetector import MSERDetector
import MaskUtils
import os
from ProgressBar import printProgressBar
import shutil

# devuelve el area de la region
# recibe la region
# cada region esta compuesta por y1,y2,x1,x2
def area(region):
    y1, y2, x1, x2 = region
    return (y2 - y1) * (x2 - x1)

# indica si una region1 esta contenida en region2
# recibe region1, region2
def esta_solapada(region_peq, region_grande):
    centro_peq = ((region_peq[0] + region_peq[1]) // 2, (region_peq[2] + region_peq[3]) // 2)
    return (region_grande[0] <= centro_peq[0] <= region_grande[1]) and (
            region_grande[2] <= centro_peq[1] <= region_grande[3])

# devuelve la mejor detección entre deteccion1 y deteccion2
# recibe deteccion1, deteccion2
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

# devuelve las detecciones filtradas
# recibe las detecciones a filtrar
# las detecciones filtradas son detecciones donde no hay solapamiento
def filter_detections(detecciones):
    filtered_detections = []
    while detecciones:
        deteccion1 = detecciones.pop()
        overlap_regions = []

        # obtiene las detecciones solapadas con deteccion1
        for deteccion2 in detecciones:
            if esta_solapada(deteccion1[0], deteccion2[0]) or esta_solapada(deteccion2[0], deteccion1[0]):
                overlap_regions.append(deteccion2)
        
        # obtener la mejor deteccion entre las detecciones solapadas y elimina las otras
        mejor = deteccion1
        while overlap_regions:
            other = overlap_regions.pop()
            detecciones.remove(other)
            mejor = obtener_mejor_parecido(mejor, other)
        filtered_detections.append(mejor)
    return filtered_detections

class Detector:
    # constructor
    def __init__(self):
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, Constants.KERNEL_SIZE)
        # mascaras medias
        self.avg_masks = {1: np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype=float),
                          2: np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype=float),
                          3: np.zeros((Constants.DIM_X, Constants.DIM_Y), dtype=float)}
        self.mser = MSERDetector() # mser
        # rango de colores para la generacion de las mascaras de color rojo
        self.color_ranges = [[np.array([160, 40, 10]), np.array([180, 255, 255])], [np.array([0, 40, 10]), np.array([10, 255, 255])]]

    # fase de entrenamiento del detector con las imagenes de entrenamiento
    # recibe image_type_map, un mapa donde key es el tipo de señal y valor son las señales de ese tipo
    def train(self, image_type_map):
        for img_type in image_type_map.keys():
            for image in image_type_map.get(img_type):
                self.avg_masks[img_type] += MaskUtils.getMask(image, self.color_ranges)
            self.avg_masks[img_type] = self.avg_masks[img_type] / 255
            self.avg_masks[img_type] = np.array(self.avg_masks[img_type] > round(self.avg_masks[img_type].mean()), dtype=float)
            self.avg_masks[img_type] = cv2.morphologyEx(self.avg_masks[img_type], cv2.MORPH_OPEN, self.kernel, iterations=1)

    # devuelve las detecciones que superan la tasa minima de acierto
    # recibe image, la imagen a procesar
    def detect(self, image):
        # deteccion de regiones con mser
        interest_regions = self.mser.applyMser(ImageUtils.equalize(image))
        detecciones = []
        for region in interest_regions:
            # redimensionar la region y obtener la mascara de rojo de la imagen
            img_cropped = ImageUtils.crop(image, region)
            img_resized = ImageUtils.resize(img_cropped)
            mask = MaskUtils.getMask(img_resized, self.color_ranges)
            # obtener el valor de parecido de la mascara con las mascaras medias
            match_rates_scores = np.array([MaskUtils.getMatchRate(mask, avg_mask) for avg_mask in list(self.avg_masks.values())])
            match_rates = np.array([mrs[0] for mrs in match_rates_scores])
            scores = np.array([mrs[1] for mrs in match_rates_scores])
            pos = scores.argmax()
            match_rate = match_rates[pos]
            # eliminar detecciones que no superan la tasa minima de aciertos
            if match_rate >= Constants.MIN_MATCH_RATE:
                detecciones.append((region, match_rate, pos+1))
        return filter_detections(detecciones) # devolver las detecciones filtradas

    # carga las imagenes de entrenamiento y entrena el detector
    # recibe la ruta del directorio de entrenamiento
    def train_from_dir(self, train_dir):
        self.train(ImageUtils.load_images(train_dir))
 
    # detecta las señales que hay en las imagenes de un directorio y genera las salidas
    # recibe la ruta del directorio que contiene las imagenes
    # guarda información de las señales detectadas en resultados.txt y resultados_por_tipo.txt 
    # guarda las imagenes que contienen las detecciones enmarcadas que superan la tasa minima
    def detect_from_dir(self, test_dir):
        # crea los ficheros de texto para las salidas
        output_file = open(Constants.RESULTS_FILE, "w")
        output_type_file = open(Constants.RESULTS_TYPE_FILE, "w")
        
        # crea el directorio para guardar las imagenes con las detecciones enmarcadas
        if os.path.exists(Constants.RESULTS_DIR):
            shutil.rmtree(Constants.RESULTS_DIR)
        os.mkdir(Constants.RESULTS_DIR)
        
        img_paths = ImageUtils.load_paths(test_dir) #obtiene las rutas de las imagenes de test
        i = 0
        total = len(img_paths)
        for img_path in img_paths:
            i += 1
            printProgressBar(i, total, prefix='Progreso:', suffix='completado', length=50)
            # carga la imagen
            img = ImageUtils.read(img_path)
            img_rectangle = img.copy()
            img_name = os.path.basename(img_path)

            # genera las salidas
            for detec in self.detect(img): # analiza la imagen
                # enmarca las regiones detectadas en la imagen
                img_rectangle = ImageUtils.drawRectangle(img_rectangle, detec[0])
                y1, y2, x1, x2 = detec[0] # genera las salidas de los ficheros de texto
                match_rate = detec[1]
                tipo = detec[2]
                output_line = img_name + ";" + str(x1) + ";" + str(y1) + ";" + str(x2) + ";" + str(y2) + ";" + str(
                    1) + ";" + str(round(match_rate * 100, 2)) + '\n'
                output_file.write(output_line)
                output_line = img_name + ";" + str(x1) + ";" + str(y1) + ";" + str(x2) + ";" + str(y2) + ";" + str(
                    tipo) + ";" + str(round(match_rate * 100, 2)) + '\n'
                output_type_file.write(output_line)
            
            # guarda la imagen con las detecciones enmarcadas
            image_save_dir = os.path.join(Constants.RESULTS_DIR, img_name)
            ImageUtils.save(img_rectangle, image_save_dir)
        output_file.close()
        output_type_file.close()
