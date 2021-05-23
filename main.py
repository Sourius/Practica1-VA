import argparse
from random import random
from colorsys import hsv_to_rgb
from TSDetector import TSDetector

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

	#crear detector
	detector = TSDetector()
	#entrenar
	print("Entrenando...")
	detector.generateAverageMasks(args.train_path)
	#probar
	print("Procesando imagenes...")
	detector.detectar_senales_directorio(args.test_path)
	print("Imagenes procesadas.")
	#fin
