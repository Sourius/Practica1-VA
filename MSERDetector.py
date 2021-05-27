import cv2
import Constants

# devuelve las coordenadas de la region detectada en la imagen con mser
# recibe el poligono y la imagen
# codigo obtenido de los apuntes de la teoria de VA
def getRegions(polygon, img):
    x, y, w, h = cv2.boundingRect(polygon)
    ratio_margin = 0.1  # margen de proporcion
    ratio = h / w  # proporcion
    crop_margin_p100_range = (5, 21)  # % del margen del recorte de la zona de interes

    for i in range(crop_margin_p100_range[0], crop_margin_p100_range[1], 5):
        crop_margin_p100 = i
        crop_margin_x = w * crop_margin_p100 // 100  # margen lateral
        crop_margin_y = h * crop_margin_p100 // 100  # margen superior/interior

        # filtrar regiones
        if 1 - ratio_margin < ratio < 1 + ratio_margin:
            # recortar
            y1 = y - crop_margin_y
            y2 = y + h + crop_margin_y
            x1 = x - crop_margin_x
            x2 = x + w + crop_margin_x

            if (y1 < 0) or (x1 < 0) or (y2 > img.shape[0]) or (x2 > img.shape[1]):  # deshacer margenes porque no caben
                y1 = y
                y2 = y + h
                x1 = x
                x2 = x + w
            return y1, y2, x1, x2


class MSERDetector:
	# constructor
    def __init__(self):
		# inicializa mser
        self.mser = cv2.MSER_create(_delta=Constants.MSER_DELTA, _max_variation=Constants.MSER_VARIATION, _min_area=Constants.MSER_MIN_AREA, _max_area=Constants.MSER_MAX_AREA)

    # devuelve las regiones detectadas con mser
	# recibe la imagen
	# codigo obtenido de los apuntes de la teoria de VA
    def applyMser(self, img):
        interest_regions = []
        polygons = self.mser.detectRegions(img) # detectar regiones con mser
        for polygon in polygons[0]:
            region_cropped = getRegions(polygon, img) # obtener las coordenadas: y1,y2,x1,x2
            if region_cropped is not None: # filtrar regiones
                interest_regions.append(region_cropped)
        return interest_regions
