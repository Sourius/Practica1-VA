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

    print("Aviso: Para que el programa funcione correctamente debe incluir el fichero entrada.txt proporcionado con "
          "la entrega en la carpeta raiz del proyecto!")
    
    # inicializar mser
    # delta 5, variation 1, area 2000
    delta = Constants.MSER_DELTA
    variation = Constants.MSER_VARIATION
    area = Constants.MSER_MIN_AREA
    # crear mascaras medias
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, Constants.KERNEL_SIZE)
    detector = TSDetector(kernel, Constants.DIM_X, Constants.DIM_Y, Constants.MIN_MATCH_RATE, delta, variation, area)
    print("Entrenando...")
    detector.generateAverageMasks(args.train_path, Constants.LEARNING_LOCATIONS_TXT)
    print("Procesando imagenes...")
    detector.detectar_senales_directorio(args.test_path)
    print("Imagenes procesadas.")
    
    # Evaluate sign detections
