# parametros para mser
MSER_DELTA = 4
MSER_VARIATION = 1
MSER_MIN_AREA = 150
MSER_MAX_AREA = 2000
#tamaño utilizado a la hora de recortar las imagenes y generar las mascaras
DIM_X = 50 # width
DIM_Y = 50 # height
KERNEL_SIZE = 3, 3 # tamaño del kernel utilizado en la apertura
MIN_MATCH_RATE = 0.35  # tasa minima de acierto [0-1]
RESULTS_DIR = "resultado_imgs" # directorio donde se guardan las imagenes con las detecciones
RESULTS_FILE = "resultado.txt" # fichero de texto donde se guardan las detecciones
RESULTS_TYPE_FILE = "resultado_por_tipo.txt" # fichero de texto donde se guardan las detecciones y el tipo de señal