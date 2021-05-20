# Detección de señales
## Introducción
<p>
Se ha implementado un detector de señales de tráfico (3 tipos: prohibición, peligro, stop) con el detector MSER. 

- A partir de un directorio con imágenes de entrenamiento, se procesan las imágenes para detectar imágenes similares.
- A partir de un directorio de prueba, se procesan las imágenes para detectar las señales presentes en las mismas. 
 
 
## Funcionamiento
A partir de un directorio con imágenes de entrenamiento, se procesan las imágenes para crear las máscaras para la detección de señales. A partir de un directorio de prueba, se procesan las imágenes para detectar las señales. 
 
El programa da como salida: 
- un archivo de texto con información acerca de las detecciones (posición de la señal dentro de la imagen, acierto al reconocer la señal)
- un archivo de texto que contiene la misma información que el mencionado anteriormente e incluye el tipo de señal detectada (1: prohibición, 2: peligro, 3: stop)
- y un directorio con las imágenes que contienen las detecciones enmarcadas.


### Ejecución
Para poner en marcha el detector, se debe ejecutar el programa principal (main.py) con 3 argumentos: train_path (directorio donde se ubican las imágenes de entrenamiento, por defecto: train_recortadas), test_path (directorio donde se encuentran las imágenes de prueba, por defecto: test), detector. Hemos implementado un único detector, por lo tanto, no es necesario pasarle el tercer parámetro (detector) a la hora de ejecutar el programa. 

<b>Importante:</b> Para calcular las máscaras medias se utiliza un archivo de texto <b><i>entradas.txt</i></b> que contiene los nombres de los directorios con cada tipo de señal a detectar (por ejemplo: “1;00;01;02”, indica que las imágenes de las señales de tipo 1, se encuentran en el subdirectorio 00, 01, y 02  del directorio de entrenamiento). Este fichero se proporciona junto con el código y es similar a <b><i>gt.txt</i></b>.

### Problemas
El detector tiene varios fallos:
- El detector no es capaz de detectar varias señales por los siguientes motivos:
  - el brillo
  - el rango de colores utilizados
  - el mser no detecta algunas señales

- Para poder detectar señales con tono oscuro y con bordes difuminados se ha ampliado el rango de valores de saturación y brillo que provoca un gran número de casos de falsos positivos:
  - se detectan regiones que no son señales con un parecido muy alto
- Mser detecta muchas regiones, algunas de esas detecciones son del mismo elemento pero con distinto tamaño que provoca que se detecten varias veces la misma señal. Hay detecciones de señales con una parte de la señal
  - no se detecta la señal completa, se detecta sólo una parte de ella porque el % de parecido de la parte pequeña es más alta que la de la señal completa
- Se detectan señales pero de tipo incorrecto por ejemplo señales de peligro y prohibición que se detectan como stop

### Mejoras
Para mejorar la detección se puede:
- normalizar los valores de los colores para que el detector sea menos sensible a la diferencia de brillo y para poder detectar bien tanto las señales oscuras como las señales claras
- mejorar la creación de la máscara de rojo para que el parecido de la señal entera sea mejor que la de una parte de la señal
- mejorar la detección de forma que el detector sea menos sensible al escalado
- añadir distintos tipos de filtros
- mejorar la detección con mser
- utilizar otros detectores aparte de mser
- modificar la implementación para que el detector vaya aprendiendo
  - ir modificando las máscaras medias con las detecciones buenas (que superen un cierto límite por ejemplo 70%) a la hora de detectar las señales

 
### Implementación
El detector se ha implementado utilizando programación orientada a objetos con python. El detector se compone de las siguientes clases:
- MserDetector: Se utiliza para detectar y obtener las regiones que hay en una imagen.
- MaskMaker: Se utiliza para obtener la máscara de una imagen.
- AverageMask: Representa una máscara media. Cada máscara media se distingue de la otra con el valor de TSType.
- TSType: Representa cada tipo de señal 1 “Prohibición”, 2 “Peligro” y 3 “Stop”.
- TransportSignal: Representa las detecciones. Se utiliza para guardar información de cada detección.
- TSDetector: Contiene toda la funcionalidad necesaria. Utiliza internamente las otras clases y permite analizar las señales a partir de un directorio y genera las salidas.
- Constants: Contiene los valores de las constantes utilizadas dentro del programa: las dimensiones de las máscaras, el valor de delta, varianza y la área para la detección de regiones con mser, el tamaño del kernel, el valor de min match rate y los nombres de los ficheros y el directorio donde se guardan las salidas.
- ProgressBar: Se utiliza para mostrar cómo va el proceso de análisis por la consola.  El código de esta clase fue obtenido de <a href="https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console">aquí</a>.

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
Las estadísticas siguientes han sido generadas con las detecciones que han superado el 35% (min match rate) de parecido con las máscaras medias calculadas y usando los rangos de color rojo en HSV que se muestran a continuación:
![image](https://user-images.githubusercontent.com/47939220/119051881-0d221c80-b9c4-11eb-89de-9039b35b0595.png)

Los resultados del análisis han sido los siguientes:
![image](https://user-images.githubusercontent.com/47939220/119051984-3347bc80-b9c4-11eb-95df-e8f232faa1f9.png)

Como se puede observar a partir de los datos, aunque el detector tiene un recall relativamente bueno, la precisión y el f1 score cae enormemente debido al alto número de falsos positivos, es decir, regiones detectadas como señales que no lo son en realidad. Esto se debe principalmente a que ciertas zonas con colores anaranjados y rojizos confunden al detector, por ejemplo: luces de semáforos, escenas otoñales, escenas con muchas luces y sombras. Se podría reducir este número de detecciones incorrectas si se aumentara el umbral de coincidencia o si se acotaran los rangos de colores, pero esto conlleva a detectar menos señales ya que hay algunas señales poco visibles incluso para el ojo humano.

Para la puntuación final nos basaremos en la completitud del detector, restando las señales detectadas de las señales que no se detectaron (ponderan -0,25) y comparándolo con el total: 
- puntuación=  señales detectadas - 0,25 * señales no detectadasseñales detectables * 100

Resumen del detector:

![image](https://user-images.githubusercontent.com/47939220/119052090-583c2f80-b9c4-11eb-9289-2933e0a4518b.png)

![image](https://user-images.githubusercontent.com/47939220/119052122-6427f180-b9c4-11eb-91d7-c38abfa0ba28.png)

