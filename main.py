import argparse

import cv2
import numpy as np
import matplotlib.pyplot as plt
from random import random
from colorsys import hsv_to_rgb
import os
from TSDetector import TSDetector
from MSERDetector import MSERDetector
import Constants

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Trains and executes a given detector over a set of testing images')
    parser.add_argument(
        '--detector', type=str, nargs="?", default="MSER_TS_Detector", help='Detector string name')
    parser.add_argument(
        '--train_path', default="train_recortadas", help='Select the training data dir')
    parser.add_argument(
        '--test_path', default="test", help='Select the testing data dir')

    args = parser.parse_args()

    print("Aviso: Para que el programa funcione correctamente debe incluir el fichero entrada.txt proporcionado con la entrega en la carpeta raiz del proyecto!")
    
    detector = TSDetector(Constants.DIM_X, Constants.DIM_Y, 0.5)
    # inicializar mser
    # delta 5, variation 1, area 2000
    delta = Constants.MSER_DELTA
    variation = Constants.MSER_VARIATION
    area = Constants.MSER_MIN_AREA
    detector.setMSER(delta, variation, area)

    # crear mascaras medias
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, Constants.KERNEL_SIZE)
    detector.setMasks(kernel)
    detector.generateAverageMasks(vars(args).get("--train_path"),"entradas.txt")
    detector.detectar_señales_directorio(vars(args).get("--test_path"))

    # Evaluate sign detections





