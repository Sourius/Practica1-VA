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

def applyMser(img, delta_value, max_variation_value):
  # APLICAR MSER, FILTRAR REGIONES, RECORTAR: teoria VA
  interest_regions = []
  img_regions = np.zeros((img.shape[0],img.shape[1],3),dtype=np.uint8)
  mser = cv2.MSER_create(_delta=delta_value, _max_variation=max_variation_value, _max_area=2000)
  polygons = mser.detectRegions(img) 
  for polygon in polygons[0]:
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
      if 1-ratio_margin < ratio < 1+ratio_margin:  # filtrar regiones que tienen una proporcion poco cuadrada
        #region_cropped = img[y-crop_margin_y:y+h+crop_margin_y, x-crop_margin_x:x+w+crop_margin_x]  # extraer imagen recortada
        y1 = y - crop_margin_y
        y2 = y + h + crop_margin_y
        x1 = x - crop_margin_x
        x2 = x + w + crop_margin_x
        if (y1 < 0) or (x1 < 0) or (y2 > img.shape[0]) or (x2 > img.shape[1]): # deshacer margenes porque no caben
          y1 = y
          y2 = y + h 
          x1 = x
          x2 = x + w
        region_cropped = (y1,y2,x1,x2) # extraer coordenadas recorte
        interest_regions.append(region_cropped)
        img_regions = cv2.fillPoly(img_regions,[polygon],colorRGB)
  return img_regions, interest_regions

def getMask(image):
  hsv_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
  mask = cv2.inRange(hsv_image, np.array([0,25,0]), np.array([10,125,50])) + cv2.inRange(hsv_image, np.array([150,50,50]), np.array([190,160,130])) + cv2.inRange(hsv_image, np.array([0,120,50]), np.array([10,255,255])) + cv2.inRange(hsv_image, np.array([320,20,60]), np.array([340,40,80]))
  return mask

# calcular la mascara media
mask_dim_x, mask_dim_y = 50,50
masks = []
average_mask_or = np.zeros((mask_dim_x, mask_dim_y), dtype=bool)
average_mask_or_t = np.zeros((mask_dim_x, mask_dim_y), dtype=bool)
average_mask_or_st = np.zeros((mask_dim_x, mask_dim_y), dtype=bool)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))

for i in range(1,6):
  path = 's'+str(i)+'.ppm'
  original = cv2.imread(path,1)
  original = cv2.resize(original, (mask_dim_x, mask_dim_y))
  # mascara de color rojo: es un array con 255 en las posiciones rojas y 0 en las demas. Dimension= (mask_dim_x,mask_dim_y)
  red_mask =  getMask(original)/255
  average_mask_or = average_mask_or + red_mask

for i in range(0,7):
  path = 't'+str(i)+'.ppm'
  original = cv2.imread(path,1)
  original = cv2.resize(original, (mask_dim_x, mask_dim_y))
  # mascara de color rojo: es un array con 255 en las posiciones rojas y 0 en las demas. Dimension= (mask_dim_x,mask_dim_y)
  red_mask =  getMask(original)/255
  average_mask_or_t = average_mask_or_t + red_mask

for i in range(0,10):
  path = 'st'+str(i)+'.ppm'
  original = cv2.imread(path,1)
  original = cv2.resize(original, (mask_dim_x, mask_dim_y))
  # mascara de color rojo: es un array con 255 en las posiciones rojas y 0 en las demas. Dimension= (mask_dim_x,mask_dim_y)
  red_mask =  getMask(original)/255
  average_mask_or_st = average_mask_or_st + red_mask

# aplicar la media y la apertura para filtrar la mascara y eliminar ruido
average_mask_or = np.array(average_mask_or > round(average_mask_or.mean()) ,dtype=float)
average_mask_or = cv2.morphologyEx(average_mask_or, cv2.MORPH_OPEN, kernel)

average_mask_or_t = np.array(average_mask_or_t > round(average_mask_or_t.mean()) ,dtype=float)
average_mask_or_t = cv2.morphologyEx(average_mask_or_t, cv2.MORPH_OPEN, kernel)

average_mask_or_st = np.array(average_mask_or_st > round(average_mask_or_st.mean()) ,dtype=float)
average_mask_or_st = cv2.morphologyEx(average_mask_or_st, cv2.MORPH_OPEN, kernel)

'''
plt.imshow(average_mask_or)
plt.show()
plt.imshow(average_mask_or_t)
plt.show()
plt.imshow(average_mask_or_st)
plt.show()
'''

#correlation = average_mask_or * masks[0] # correlar la mascara media con la mascara de interes (masks[0] solo es un ejemplo)
# en vez de masks[i] habria que usar imagen[a,b,c,d]. a,b,c,d = interest_regions[j]
# de esta manaera se van recortando las zonas de la imagen original y se va extrayendo y aplicando la mascara
#plt.imshow(correlation)
#plt.show()
#print("Coincidencias: " , np.sum(correlation))  # sumar las coincidencias para saber cuantos "pixeles" han coincidido

def matchRate(mask, fit_mask):
  correlation = mask * fit_mask
  return np.count_nonzero(correlation)/np.count_nonzero(fit_mask)

def area(region):
  y1, y2, x1, x2 = region
  return (y2 - y1) * (x2 - x1)

# el boolean indica si es una region repetida
# el indice indica la posicion de la lista donde hay que almacenar el mejor valor o -1 si es una señal nueva --> region nueva
def obtener_mejor_parecido(region, match_rate, lista_regiones):
  i = -1
  for region_antigua, match, _ in lista_regiones:
    i += 1
    if (esta_solapada(region,region_antigua) or esta_solapada(region_antigua,region)):
      area_antigua = area(region_antigua)
      area_nueva = area(region)
      proporcion = area_nueva / area_antigua
      if (proporcion > 2):  # es mucho mas grande
        return True, i, (region, match_rate)
      elif (match_rate > match): 
        return True, i, (region, match_rate)
      else: 
        return True, i, (region_antigua, match)
  return False, -1, (region, match_rate)

# detectar si estan solapadas mediante el centro de cada una
def esta_solapada(region_peq, region_grande):
  centro_peq = ((region_peq[0] + region_peq[1])//2, (region_peq[2] + region_peq[3])//2)
  return (region_grande[0] <= centro_peq[0] <= region_grande[1]) and (region_grande[2] <= centro_peq[1] <= region_grande[3])

def detectar_señales(img_path,min_match_rate):
  original = cv2.imread(img_path,1)
  original_rgb = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2RGB)
  original_gray = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2GRAY)
  img_eq = cv2.equalizeHist(original_gray)
  img_mser, interest_regions = applyMser(img_eq,5,1.0)

  """
  plt.imshow(img_mser)
  plt.show()

  plt.imshow(original_rgb)
  plt.show()
  """

  detecciones = []
  tipo = -1
  for region in interest_regions:
    y1,y2,x1,x2 = region
    original_cropped = cv2.resize(original[y1:y2, x1:x2], (50, 50))
    original_cropped_hsv = cv2.cvtColor(original_cropped.copy(), cv2.COLOR_BGR2HSV)

    mask = getMask(original_cropped)
    mask_c =  mask * average_mask_or
    mask_t =  mask * average_mask_or_t
    mask_st =  mask * average_mask_or_st
    
    match_rate_c = matchRate(mask_c, average_mask_or)
    match_rate_t = matchRate(mask_t, average_mask_or_t)
    match_rate_st = matchRate(mask_st, average_mask_or_st)

    match_rates = np.array([match_rate_c, match_rate_t, match_rate_st])
    tipo = match_rates.argmax() + 1 # tipo de señal
    match_rate = match_rates[tipo-1]

    """
    plt.title(str(original_cropped_hsv[5,5]) + "match: " + str(match_rate))
    plt.imshow(original_rgb[y1:y2, x1:x2])
    plt.show()
    plt.imshow(masks[tipo])
    plt.show()
    """

    if (match_rate >= min_match_rate):
      repetida, indice, mejor_parecido = obtener_mejor_parecido(region, match_rate, detecciones)
      if (repetida):
        detecciones[indice] = (mejor_parecido[0], mejor_parecido[1], tipo)
      else:
        detecciones.append((mejor_parecido[0], mejor_parecido[1], tipo))
    #detecciones.append((region, match_rate))
  return detecciones

#pruebas con imagenes
img_path = '00009.ppm'
#img_path = '00115.ppm'
original = cv2.imread(img_path,1)
original_rgb = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2RGB)
#min_match_rate = 0.45
min_match_rate = 0.25
detecciones = detectar_señales(img_path, min_match_rate)

for deteccion in detecciones:
  y1,y2,x1,x2 = deteccion[0]
  centro = ((y1+y2)//2,(x1+x2)//2)
  plt.title(img_path + " - Acierto: " + str(round(deteccion[1]*100,2))+'% - tipo: ' + str(deteccion[2]) + " - region: " + str(deteccion[0]) + " - centro: " + str(centro))
  plt.imshow(original_rgb[y1:y2, x1:x2])
  plt.show()

for i in range(0,10):
  img_path = '0000'+str(i)+'.ppm'
  original = cv2.imread(img_path,1)
  original_rgb = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2RGB)
  #min_match_rate = 0.45
  min_match_rate = 0.40
  detecciones = detectar_señales(img_path, min_match_rate)
  for deteccion in detecciones:
    y1,y2,x1,x2 = deteccion[0]
    plt.title(img_path + " - Acierto: " + str(round(deteccion[1]*100,2))+'% - tipo: ' + str(deteccion[2]))
    plt.imshow(original_rgb[y1:y2, x1:x2])
    plt.show()

for i in range(10,21):
  img_path = '000'+str(i)+'.ppm'
  original = cv2.imread(img_path,1)
  original_rgb = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2RGB)
  #min_match_rate = 0.45
  min_match_rate = 0.40
  detecciones = detectar_señales(img_path, min_match_rate)
  for deteccion in detecciones:
    y1,y2,x1,x2 = deteccion[0]
    plt.title(img_path + " - Acierto: " + str(round(deteccion[1]*100,2))+'% - tipo: ' + str(deteccion[2]))
    plt.imshow(original_rgb[y1:y2, x1:x2])
    plt.show()
