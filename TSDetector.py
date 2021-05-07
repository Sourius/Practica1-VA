from MSERDetector import MSERDetector
from AverageMask import AverageMask
from TSType import TSType
from MaskMaker import MaskMaker
import os
import cv2
import numpy as np
from TransportSignal import TransportSignal
import matplotlib.pyplot as plt
from PIL import Image
import Constants
from ProgressBar import printProgressBar


class TSDetector:
    def __init__(self, dim_x, dim_y, mmr):
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.min_match_rate = mmr
        if not os.path.exists(Constants.RESULTS_DIR):
            os.makedirs(Constants.RESULTS_DIR)

    # inicializar mser
    def setMSER(self, delta, variation, area):
        self.mser = MSERDetector(delta, variation, area);

    # inicializar las mascaras medias
    def setMasks(self, kernel):
        self.kernel = kernel;
        # danger, prohibition, stop
        self.avg_pmask = AverageMask(kernel, TSType.PROHIBICION, self.dim_x, self.dim_y);
        self.avg_dmask = AverageMask(kernel, TSType.PELIGRO, self.dim_x, self.dim_y);
        self.avg_smask = AverageMask(kernel, TSType.STOP, self.dim_x, self.dim_y);
        self.generador = MaskMaker(kernel, self.dim_x, self.dim_y);

    # añade rango de colores que se tienen en cuenta a la hora de detectar la señal
    def addColorRange(self, lower, higher):
        self.generador.addHSVRange(lower, higher);

    def __loadLearningImages(self, dir_path, tipo):
        # obtener lista de ficheros
        dir_path = 'train_recortadas/' + dir_path
        ficheros = os.listdir(dir_path)
        for fichero in ficheros:
            # obtener la ruta de la imagen
            image_path = os.path.join(dir_path, fichero)

            if os.path.isfile(image_path) and fichero.endswith('.ppm'):
                # obtener imagen y redimensionar
                original = cv2.imread(image_path, 1)
                resized_image = cv2.resize(original, (self.dim_x, self.dim_y))
                tipo = int(tipo)
                # añadir imagen
                if tipo == int(self.avg_pmask.getType().value):
                    self.avg_pmask.add_learning_image(resized_image);
                elif tipo == int(self.avg_dmask.getType().value):
                    self.avg_dmask.add_learning_image(resized_image);
                elif tipo == int(self.avg_smask.getType().value):
                    self.avg_smask.add_learning_image(resized_image);

    # carga las imagenes segun el <fichero>.txt y genera la mascara media de las tres señales
    def generateAverageMasks(self, file_path):
        # leer del fichero txt
        f = open(file_path, mode='r', encoding='utf-8')
        # leer lineas
        for line in f:
            # obtener tipo
            ficheros = line.split(";")
            tipo = ficheros[0]
            # añadir imagenes de aprendizaje
            for i in range(1, len(ficheros)):
                # leer la ruta de cada fichero
                file_path = ficheros[i].strip()
                self.__loadLearningImages(file_path, tipo)

        # calcular mascara media
        self.avg_dmask.generateAVGMask();  # peligro
        #plt.imshow(self.avg_dmask.getValue())
        #plt.show()
        self.avg_pmask.generateAVGMask();  # prohibición
        #plt.imshow(self.avg_pmask.getValue())
        #plt.show()
        self.avg_smask.generateAVGMask();  # stop
        #plt.imshow(self.avg_smask.getValue())
        #plt.show()
        f.close();

    # calcular area
    def __getArea(self, region):
        y1, y2, x1, x2 = region
        return (y2 - y1) * (x2 - x1)

    # obtener el % de parecido
    def getMatchRate(self, mask, fit_mask):
        correlation = mask * fit_mask
        area_correlation = np.count_nonzero(correlation)
        area_fit_mask = np.count_nonzero(fit_mask)
        return area_correlation / area_fit_mask, area_correlation

    # indica si hay que modificar, y nos devuelve la posicion de la señal que hay que modificar con su rergio y match rate
    # devuelve true o false que indica si hay que añadir o no
    # devuele el indice --> key
    def __obtener_mejor_parecido(self, region, match_rate, lista_signals):
        i = -1
        for ts in lista_signals:
            i += 1
            region_antigua = ts.getRegion();
            match = ts.getRating();
            # si esta solapada
            if (self.__esta_solapada(region, region_antigua) or self.__esta_solapada(region_antigua, region)):
                area_antigua = self.__getArea(region_antigua)
                area_nueva = self.__getArea(region)
                # calcular proporcion de tamaño entre los dos
                proporcion = area_nueva / area_antigua
                # si es mucho mas grande
                if (proporcion > 2):
                    return True, i, (region, match_rate);
                elif (match_rate > match):
                    return True, i, (region, match_rate)
                else:
                    return False, i, (region_antigua, match);
        return True, -1, (region, match_rate)

    # indica si una region esta solapada sobre la otra, utiliza el centro de la región para detectarlo
    def __esta_solapada(self, region_peq, region_grande):
        centro_peq = ((region_peq[0] + region_peq[1]) // 2, (region_peq[2] + region_peq[3]) // 2)
        return (region_grande[0] <= centro_peq[0] <= region_grande[1]) and (
                    region_grande[2] <= centro_peq[1] <= region_grande[3])

    # detectar señales apartir de un directorio y guardar las detecciones en un atributo
    def detectar_señales_directorio(self, dir_imagenes):
        imagenes_test = os.listdir(dir_imagenes)
        output_file = open("salida.txt", "w")
        i = 0
        total = len(imagenes_test)
        for imagen in imagenes_test:
            i += 1
            printProgressBar(i, total, prefix='Progreso:', suffix='completado', length=50)
            # obtener la ruta de la imagen
            image_path = os.path.join(dir_imagenes, imagen)
            if os.path.isfile(image_path) and image_path.endswith('.jpg'):
                detecciones = self.detectar_señales(image_path)
                img = cv2.imread(image_path, 1)
                img_color = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
                img_color_rectangle = img.copy()
                for ts in detecciones:
                    upper_left, lower_right = ts.getCorners()
                    img_color_rectangle = cv2.rectangle(img_color_rectangle, upper_left, lower_right, (0,0,255), 4)
                    output_file.write(ts.getResult()+'\n')
                    #print(ts.getResult())
                    #y1, y2, x1, x2 = ts.getRegion()
                    #plt.title(ts.getResult())
                    #plt.imshow(img_color[y1:y2, x1:x2])
                    #plt.show()
                image_save_dir = os.path.join(Constants.RESULTS_DIR, os.path.basename(image_path))
                #print('guardando en ', image_save_dir)
                cv2.imwrite(image_save_dir, img_color_rectangle)
        output_file.close()
    # generar resultado --> ap 5

    # detecta señales de una imagen y devuelve las señales detectadas en un diccionario
    def detectar_señales(self, img_path):
        img = cv2.imread(img_path, 1)
        img_color = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
        img_gray = cv2.cvtColor(img_color.copy(), cv2.COLOR_BGR2GRAY)
        img_eq = cv2.equalizeHist(img_gray)
        img_mser, interest_regions = self.mser.applyMser(img_eq)

        # utilizar diccionario --> guardar señal segun el tipo de señal
        detecciones = [];
        for region in interest_regions:
            y1, y2, x1, x2 = region
            img_cropped = cv2.resize(img[y1:y2, x1:x2], (self.dim_x, self.dim_y))
            img_cropped_hsv = cv2.cvtColor(img_cropped.copy(), cv2.COLOR_BGR2HSV)

            mask = self.generador.getMask(img_cropped);
            average_masks = [self.avg_pmask.getValue(), self.avg_dmask.getValue(), self.avg_smask.getValue()]
            match_rates_scores = np.array([self.getMatchRate(mask, avg_mask) for avg_mask in average_masks])
            match_rates = np.array([mrs[0] for mrs in match_rates_scores])
            scores = np.array([mrs[1] for mrs in match_rates_scores])
            tipo = scores.argmax()  # el tipo se definira segun la mascara mas grande
            match_rate = match_rates[tipo]

            if (match_rate >= self.min_match_rate):
                addSignal, indice, mejor_parecido = self.__obtener_mejor_parecido(region, match_rate,
                                                                                  detecciones);  # utilizar diccionario
                tsType = TSType(tipo + 1)
                ts = TransportSignal(tsType, mejor_parecido[1], img_path, mejor_parecido[0]);
                if indice == -1:
                    detecciones.append(ts);
                elif addSignal:
                    detecciones[indice] = ts;
        return detecciones