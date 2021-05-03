# -*- coding: utf-8 -*-
"""
@author: chris-bena
@author: sourius
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from random import random
from colorsys import hsv_to_rgb
from enum import Enum, unique
import os

# MSER
class MSERDetector:
    def __init__(self, delta, variation, area):
        self.setMSER(delta, variation, area);

    def setMSER(self, delta, variation, area):
        self.mser = cv2.MSER_create(_delta=delta, _max_variation=variation, _max_area=area)

    # APLICAR MSER
    def __detectRegions(self, img):
        interest_regions = np.zeros((img.shape[0],img.shape[1],3),dtype=np.uint8)
        return self.mser.detectRegions(img) 
   
    # RECORTAR
    def __cropRegion(self, polygon, img):    
        colorRGB = hsv_to_rgb(random(),1,1)
        colorRGB = tuple(int(color*255) for color in colorRGB)
        x,y,w,h = cv2.boundingRect(polygon)
        ratio_margin = 0.1  # margen de proporcion
        ratio = h/w  # proporcion
        crop_margin_p100_range = (5, 21) # % del margen del recorte de la zona de interes
    
        for i in range(crop_margin_p100_range[0], crop_margin_p100_range[1], 5):
            crop_margin_p100 = i
            crop_margin_x = w*crop_margin_p100//100  # margen lateral
            crop_margin_y = h*crop_margin_p100//100  # margen superior/interior
            
            # filtrar regiones
            if 1-ratio_margin < ratio < 1+ratio_margin:
                #recortar
                y1 = y - crop_margin_y
                y2 = y + h + crop_margin_y
                x1 = x - crop_margin_x
                x2 = x + w + crop_margin_x
    
                if (y1 < 0) or (x1 < 0) or (y2 > img.shape[0]) or (x2 > img.shape[1]): # deshacer margenes porque no caben
                    y1 = y
                    y2 = y + h 
                    x1 = x
                    x2 = x + w
                return (y1,y2,x1,x2)

    def __getRandomColor(self):
        colorRGB = hsv_to_rgb(random(),1,1)
        return tuple(int(color*255) for color in colorRGB)

    # APLICAR MSER, FILTRAR REGIONES, RECORTAR: teoria VA
    def applyMser(self,img):
        img_regions = np.zeros((img.shape[0],img.shape[1],3),dtype=np.uint8)
        polygons = self.__detectRegions(img);
        interest_regions = []
        for polygon in polygons[0]:
            region_cropped = self.__cropRegion(polygon, img);
            interest_regions.append(region_cropped)
            img_regions = cv2.fillPoly(img_regions,[polygon],self.__getRandomColor())
        return img_regions, interest_regions

#tipo de señal
@unique
class TSType(Enum):
	def __str__(self):
		return str(self.value);
	PROHIBICION = 1
	PELIGRO = 2
	STOP = 3

#señal detectada
class TransportSignal:	
    def __init__(self, ts_type, rating, image, region):
        self.setType(ts_type) #tipo de señal
        self.setRating(rating) # puntuacion de la imagen
        self.setImage(image) # nombre de la imagen
        self.setRegion(region) # region de la señal y1,y2,x1,x2

    def getType(self):
        return self.ts_type;

    def setType(self, ts_type):
        if isinstance(ts_type, TSType):
            self.ts_type = ts_type;

    def getRating(self):
        return self.rating;

    def setRating(self, rating):
        if(isinstance(rating, float)):
            self.rating = rating;

    def getImage(self):
        return self.image

    def setImage(self, image):
        if(isinstance(image, str)):
            self.image = image

    def getRegion(self):
        return self.region

    def setRegion(self, region):
        if(isinstance(region, tuple)):
            y1,y2,x1,x2 = region
            self.region = region

    def getResult(self):
        # devolver resultado como nos pide en el enunciado
        y1,y2,x1,x2 = self.getRegion();
        return self.image+";"+str(x1)+";"+str(y1)+";"+str(x2)+";"+str(y2)+";"+str(self.getType())+";"+str(self.getRating()*100);

class MaskMaker:
    def __init__(self, kernel, dim_x, dim_y):
        self.kernel = kernel;
        self.dim_x = dim_x;
        self.dim_y = dim_y;
        self.ranges = [];
        self.__setRedColor();
	
    #inicializar rango de colores a rojo
    def __setRedColor(self):
        #posibles valores de los rojo
        #H 0 a 10 y 160 a 180 en openCV
        #S >= 40
        #V >= 30
        self.addHSVRange(np.array([0,70,30]), np.array([10,255,255]));
        self.addHSVRange(np.array([160,70,30]), np.array([179,255,255]));

    def addHSVRange(self, low_range, high_range):
        self.ranges.append((low_range, high_range));

    def getMask(self, image):
        hsv_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV);
        mask = np.zeros((self.dim_x,self.dim_y));
        for min_range,max_range in self.ranges:
            mask += cv2.inRange(hsv_image, min_range, max_range);
        return mask;

class AverageMask:
    def __init__(self, kernel, type, dim_x, dim_y):
        self.kernel = kernel;
        self.maskMaker = MaskMaker(kernel, dim_x, dim_y);
        self.setType(type);
        self.value = np.zeros((dim_x, dim_y), dtype=bool);
        self.avg_mask_or = np.zeros((dim_x, dim_y), dtype=bool);

    def getType(self):
        return self.ts_type;

    def setType(self, ts_type):
        if isinstance(ts_type, TSType):
            self.ts_type = ts_type;
	
    def getValue(self):
        return self.value;
	
    def add_learning_image(self, cropped_image):
        red_mask = self.maskMaker.getMask(cropped_image)
        self.avg_mask_or = self.avg_mask_or + red_mask
	
	#generar mascara media
    def generateAVGMask(self):
        self.avg_mask_or = self.avg_mask_or / 255
        self.avg_mask_or = np.array(self.avg_mask_or > round(self.avg_mask_or.mean()) ,dtype=float)
        self.value = cv2.morphologyEx(self.avg_mask_or, cv2.MORPH_OPEN, self.kernel, iterations = 1)

	#obtener el % de parecido
    def getMatchRate(self, image_mask):
        correlation = image_mask * self.value;
        return np.count_nonzero(correlation)/np.count_nonzero(self.value);

class TSDetector:
    def __init__(self, dim_x, dim_y):
        self.dim_x = dim_x
        self.dim_y = dim_y

    #inicializar mser    
    def setMSER(self, delta, variation, area):
        self.mser = MSERDetector(delta, variation, area);

    #inicializar las mascaras medias
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
        ficheros = os.listdir(dir_path)
        for fichero in ficheros:
            # obtener la ruta de la imagen
            image_path = os.path.join(dir_path, fichero)
            if os.path.isfile(image_path) and fichero.endswith('.ppm'):
                #obtener imagen y redimensionar
                original = cv2.imread(image_path,1)
                resized_image = cv2.resize(original, (self.dim_x, self.dim_y))
                
                #añadir imagen
                if tipo == self.avg_pmask.getType().value:
                    self.avg_pmask.addLearningImage(resized_image);
                elif tipo == self.avg_dmask.getType().value:
                    self.avg_dmask.addLearningImage(resized_image);
                elif tipo == self.avg_smask.getType().value:
                    self.avg_smask.addLearningImage(resized_image);
        

    # carga las imagenes segun el <fichero>.txt y genera la mascara media de las tres señales 
    def generateAverageMasks(self, file_path):
        # leer del fichero txt
        try:
            f = open(file_path, mode='r', encoding='utf-8')
            #leer lineas
            for line in f:
                #obtener tipo
                ficheros = line.split(";")
                print(str(ficheros));
                tipo = ficheros[0];
                # añadir imagenes de aprendizaje
                for i in range (1, len(ficheros)):
                    #leer la ruta de cada fichero
                    file_path = ficheros[i].strip();
                    self.__loadLearningImages(file_path, tipo)
                        
            # calcular mascara media
            self.avg_dmask.generateAVGMask(); # peligro
            self.avg_pmask.generateAVGMask(); # prohibición
            self.avg_smask.generateAVGMask(); # stop
        finally:
            f.close();

    #calcular area
    def __getArea(region):
        y1, y2, x1, x2 = region
        return (y2 - y1) * (x2 - x1)

    # indica si hay que modificar, y nos devuelve la posicion de la señal que hay que modificar con su rergio y match rate
    # devuelve true o false que indica si hay que añadir o no
    # devuele el indice --> key
    def __obtener_mejor_parecido(region, match_rate, lista_signals):
        i = -1
        for ts in lista_signals:
            i += 1
            reg = ts.getRegion();
            #si esta solapada
            if (self.__esta_solapada(region,reg) or self.__esta_solapada(reg,region)):
                area_antigua = area(region_antigua)
                area_nueva = area(region)
                #calcular proporcion de tamaño entre los dos
                proporcion = area_nueva / area_antigua
                #si es mucho mas grande
                if (proporcion > 2): 
                    return True, i, (region, match_rate);
                elif (match_rate > match): 
                    return True, i, (region, match_rate)
                else: 
                    return False, i, (region_antigua, match);
        return True, -1, (region, match_rate)

    # indica si una region esta solapada sobre la otra, utiliza el centro de la región para detectarlo
    def __esta_solapada(region_peq, region_grande):
        centro_peq = ((region_peq[0] + region_peq[1])//2, (region_peq[2] + region_peq[3])//2)
        #return (region_grande[0] < centro_peq[0] < region_grande[1]) and (region_grande[2] < centro_peq[1] < region_grande[3])
        return (region_grande[0] <= centro_peq[0] <= region_grande[1]) and (region_grande[2] <= centro_peq[1] <= region_grande[3])

    # detectar señales apartir de un directorio
    # generar resultado --> ap 5

    # detecta señales de una imagen y devuelve las señales detectadas en un diccionario
    def detectar_señales(self, img_path, min_match_rate):
        original = cv2.imread(img_path,1)
        original_rgb = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2RGB)
        original_gray = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2GRAY)
        img_eq = cv2.equalizeHist(original_gray)
        img_mser, interest_regions = self.mser.applyMser(img_eq)

        detecciones = [];
        for region in interest_regions:
            y1,y2,x1,x2 = region
            original_cropped = cv2.resize(original[y1:y2, x1:x2], (self.dim_x, self.dim_y))
            original_cropped_hsv = cv2.cvtColor(original_cropped.copy(), cv2.COLOR_BGR2HSV)
            
            mask = self.generador.getMask(original_cropped);
            match_rate_pmask = self.avg_pmask.getMatchRate(mask);
            match_rate_dmask = self.avg_dmask.getMatchRate(mask);
            match_rate_smask = self.avg_smask.getMatchRate(mask);

            match_rates = np.array([match_rate_pmask, match_rate_dmask, match_rate_smask])
            tipo = match_rates.argmax()+1
            match_rate = match_rates[tipo-1]

            if (match_rate >= min_match_rate):
                addSignal, indice, mejor_parecido = self.__obtener_mejor_parecido(region, match_rate, detecciones) # utilizar diccionario
                tsType = TSType(tipo)
                ts = TransportSignal(tsType, mejor_parecido[1], img_path, mejor_parecido[0]);
                if indice == -1:
                    detecciones.append(ts);
                elif addSignal:
                    detecciones[indice] = ts;
        return detecciones