from TSType import TSType


class TransportSignal:
    def __init__(self, ts_type, rating, image, region):
        self.setType(ts_type)  # tipo de señal
        self.setRating(rating)  # puntuacion de la imagen
        self.setImage(image)  # nombre de la imagen
        self.setRegion(region)  # region de la señal y1,y2,x1,x2

    def getCorners(self):
        y1,y2,x1,x2 = self.getRegion()
        upper_left = (x1, y1)
        lower_right = (x2 ,y2)
        return upper_left, lower_right

    def getType(self):
        return self.ts_type;

    def setType(self, ts_type):
        if isinstance(ts_type, TSType):
            self.ts_type = ts_type;

    def getRating(self):
        return self.rating;

    def setRating(self, rating):
        if (isinstance(rating, float)):
            self.rating = rating;

    def getImage(self):
        return self.image

    def setImage(self, image):
        if (isinstance(image, str)):
            self.image = image

    def getRegion(self):
        return self.region

    def setRegion(self, region):
        if (isinstance(region, tuple)):
            y1, y2, x1, x2 = region
            self.region = region

    def getResult(self):
        # devolver resultado como nos pide en el enunciado

        y1, y2, x1, x2 = self.getRegion();
        return self.image + ";" + str(x1) + ";" + str(y1) + ";" + str(x2) + ";" + str(y2) + ";" + str(
            self.getType()) + ";" + str(round(self.getRating()*100, 2))
