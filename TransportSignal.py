from TSType import TSType


class TransportSignal:
    def __init__(self, ts_type, rating, image, region):
        self.ts_type = ts_type  # tipo de señal
        self.rating = rating  # puntuacion de la imagen
        self.image = image  # nombre de la imagen
        self.region = region  # region de la señal y1,y2,x1,x2

    def getCorners(self):
        y1, y2, x1, x2 = self.getRegion()
        upper_left = (x1, y1)
        lower_right = (x2, y2)
        return upper_left, lower_right

    def getType(self):
        return self.ts_type

    def getRating(self):
        return self.rating

    def getImage(self):
        return self.image

    def getRegion(self):
        return self.region

    def getResult(self):
        # devolver resultado
        y1, y2, x1, x2 = self.getRegion()
        return self.image + ";" + str(x1) + ";" + str(y1) + ";" + str(x2) + ";" + str(y2) + ";1;" + str(
            round(self.getRating() * 100, 2))

    def getTypeResult(self):
        # devolver resultado por tipo
        y1, y2, x1, x2 = self.getRegion()
        return self.image + ";" + str(x1) + ";" + str(y1) + ";" + str(x2) + ";" + str(y2) + ";" + str(
            self.getType()) + ";" + str(round(self.getRating() * 100, 2))
