# Detección de señales
## Introducción
<p>
Se ha implementado un detector de señales de tráfico (3 tipos: prohibición, peligro, stop) con el detector MSER. 

- A partir de un directorio con imágenes de entrenamiento, se procesan las imágenes para detectar imágenes similares.
- A partir de un directorio de prueba, se procesan las imágenes para detectar las señales presentes en las mismas. 
 
El programa da como salida: un archivo de texto con información acerca de las detecciones (posición de la señal dentro de la imagen, acierto al reconocer la señal), un archivo de texto que contiene la misma información que el mencionado anteriormente e incluye el tipo de señal detectada (1: prohibición, 2: peligro, 3: stop) y un directorio con las imágenes que contienen las detecciones enmarcadas.

## Funcionamiento
### Ejecución
Para poner en marcha el detector, se debe ejecutar el programa principal (main.py) con 3 argumentos: train_path (directorio donde se ubican las imágenes de entrenamiento, por defecto: train_recortadas), test_path (directorio donde se encuentran las imágenes de prueba, por defecto: test), detector. Hemos implementado un único detector, por lo tanto, no es necesario pasarle el tercer parámetro (detector) a la hora de ejecutar el programa.

### Implementación
El detector se ha implementado utilizando programación orientada a objetos con python. El detector se compone de las siguientes clases:
- MserDetector: Se utiliza para detectar y obtener las regiones que hay en una imagen.
- MaskMaker: Se utiliza para obtener la máscara de una imagen.
- AverageMask: Representa una máscara media. Cada máscara media se distingue de la otra con el valor de TSType.
- TSType: Representa cada tipo de señal 1 “Prohibición”, 2 “Peligro” y 3 “Stop”.
- TransportSignal: Representa las detecciones. Se utiliza para guardar información de cada detección.
- TSDetector: Contiene toda la funcionalidad necesaria. Utiliza internamente las otras clases y permite analizar las señales a partir de un directorio y genera las salidas.
- ProgressBar: Se utiliza para mostrar cómo va el proceso de análisis por la consola.

Para más información pueden consultar el código.

#### Cálculo de la mascara media
Para calcular las máscaras medias se utiliza el fichero entradas.txt que contiene los nombres de los directorios con cada tipo de señal a detectar (por ejemplo: “1;00;01;02”, indica que las imágenes de las señales de tipo 1, se encuentran en el subdirectorio 00, 01, y 02  del directorio de entrenamiento). 

A partir de esta información se obtienen las imágenes de entrenamiento que están ubicadas en el train_path.
- Por cada imagen de entrenamiento:
  - Se carga la imagen
    - Se obtiene la máscara de color rojo de la imagen
    - Se suma a la máscara acumulada del tipo correspondiente
  - Al finalizar:
    - Se divide la máscara media de cada tipo entre 255 para averiguar la frecuencia de repetición de cada posición de la máscara media.
    - Se filtran las posiciones más repetidas (mayor aparición que la media)
    - Se aplica una apertura para limpiar la máscara

#### Detectar señal de cada imagen del directorio de test
A partir de test_path se obtienen las imágenes de prueba.
- Por cada imagen:
  - Detectar las regiones aplicando con el detector de regiones MSER y filtrarlas dependiendo de su relación entre la altura y la anchura.
  - Calcular la máscara de color la imagen
  - Obtener el porcentaje de parecido y el acierto total con la máscara media correspondiente. A la región detectada se le asocia el tipo de señal dependiendo de la máscara que ha tenido mayor acierto total y se le asigna una puntuación dependiendo porcentaje de parecido
  - Si la detección supera un umbral mínimo se guarda. 
      - Si se detecta solapamiento de una región nueva con otra ya almacenada, se elige la más grande (tamaño superior al doble) y en caso de no ser muy diferentes por tamaño, se elige la que tenga el mejor parecido.
  - por cada detección se generan las salidas (imagen enmarcando la detección, información de la detección en fichero de texto).

### Para implementar el funcionamiento se han empleado las funciones de Open CV siguientes:
- cv2.morphologyEx(aux, cv2.MORPH_OPEN, self.kernel, iterations=1): para aplicar apertura
- cv2.MSER_create(_delta=delta, _max_variation=variation, _max_area=area): para inicializar mser
- cv2.boundingRect(polygon): para obtener las dimensiones (altura y anchura) de las regiones detectadas
- cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV): para cambiar de un espacio de color a otro
- cv2.inRange(hsv_image, min_range, max_range): para comprobar si los valores de la imagen en hsv están entre el mínimo y el máximo (detección de color)
- cv2.imread(image_path, 1): para cargar imagen
- cv2.resize(original, (self.dim_x, self.dim_y)): para redimensionar la imagen de las señales recortadas a 50, 50
- cv2.rectangle(img_color_rectangle, upper_left, lower_right, (0, 0, 255), 4): para marcar las detecciones en la imagen en un rectángulo
- cv2.imwrite(image_save_dir, img_color_rectangle): para guardar la imagen con las detecciones enmarcadas
- cv2.equalizeHist(img_gray): para obtener la imagen ecualizada (amplia los valores del histograma) y detectar mejor las regiones con el mser

## Estadísticas de funcionamiento
Las estadísticas siguientes han sido generadas con las detecciones que han superado el 35% de parecido con las máscaras medias calculadas.

![image](https://user-images.githubusercontent.com/47939220/118286754-18aca980-b4d3-11eb-9959-bd600a2c90a2.png)

![image](https://user-images.githubusercontent.com/47939220/118286835-2a8e4c80-b4d3-11eb-8f4f-b203bebc596e.png)
