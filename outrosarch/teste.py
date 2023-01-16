from PIL import Image, ImageFilter
import cv2 as cv
import numpy as np
from math import sqrt
from itertools import product

BLACK, WHITE = 0, 255

def modaPixel(entrie: Image.Image):
  dictModa = {}
  def modaPixel(entrie: tuple):
    if entrie in dictModa:
      dictModa[entrie] += 1
      return
    dictModa[entrie] = 1
  for x in range(entrie.size[0]):
    for y in range(entrie.size[1]):
      modaPixel(entrie.getpixel((x, y)))
  return dictModa

def writeDict(entrie: dict, output: str):
  with open(output, "w") as saida:
    for key, value in entrie.items():
      saida.write(f"{key} - {value}\n")

def xFilter(entrie: Image.Image, length: int):
  def xFilter(entrie: list):
    resul = False
    for i in range(1, length - 1):
      resul = (resul or bool(entrie[i]))
    return (not bool(entrie[0]) and resul and not bool(entrie[-1]))
  output = entrie.copy()
  lista = []
  for x in range(entrie.size[0] - length + 1):
    for y in range(entrie.size[1]):
      for i in range(length):
        lista.append(entrie.getpixel((x + i, y)))
      if xFilter(lista):
        for i in range(1, length - 1):
          output.putpixel((x + i, y), WHITE)
      lista.clear()
  return output

def extract(entrie: cv.Mat, radius = 5):
  convert = rgb2gray(entrie)
  def extract(entrie: tuple[int, int]):
    def extract(entrie: tuple[int, int]):
      for x, y in product(range(-radius, radius + 1), range(1, radius + 1)):
        tupla = entrie[0] + x, entrie[1] + y
        if convert[tupla] == BLACK: return tupla
    entrada, lista = entrie, []
    lista.append(entrada)
    while True:
      entrada = extract(entrada)
      if entrada is None: break
      lista.append(entrada)
    return lista
  lista = []
  for tupla in product(range(convert.shape[0]), range(convert.shape[1] // 5)):
    if convert[tupla] == BLACK: lista.append(extract(tupla))
  with open("arquivo.txt", "w") as saida:
    for elem in sorted(lista): saida.write(f"{elem}\n")

def yFilterNoises(entrie: Image.Image, length: int):
  def yFilter(entrie: list):
    resul = False
    for i in range(1, length - 1):
      resul = (resul or bool(entrie[i]))
    return (not bool(entrie[0]) and resul and not bool(entrie[-1]))
  output = entrie.copy()
  lista = []
  for y in range(entrie.size[1] - length + 1):
    for x in range(entrie.size[0]):
      for i in range(length):
        lista.append(entrie.getpixel((x, y + i)))
      if yFilter(lista):
        for i in range(1, length - 1):
          output.putpixel((x, y + i), WHITE)
      lista.clear()
  return output

def sobelFilter(entrie: Image.Image):
  XSOBEL = ImageFilter.Kernel((3, 3), [-1, 0, 1, -2, 0, 2, -1, 0, 1], 1, 0)
  YSOBEL = ImageFilter.Kernel((3, 3), [-1, -2, -1, 0, 0, 0, 1, 2, 1], 1, 0)
  entrie = entrie.convert("L")
  xsobel, ysobel = entrie.filter(XSOBEL), entrie.filter(YSOBEL)
  output = Image.new("L", entrie.size)
  for x in range(entrie.size[0]):
    for y in range(entrie.size[1]):
      xpixel = xsobel.getpixel((x, y))
      ypixel = ysobel.getpixel((x, y))
      value = int(sqrt(xpixel**2 + ypixel**2))
      output.putpixel((x, y), min(value, 255))
  return output

def binarize(entrie: Image.Image, llevel = 80):
  def binarize(entrie: int):
    if entrie < llevel: return WHITE
    return BLACK
  output = Image.new("L", entrie.size)
  for x in range(entrie.size[0]):
    for y in range(entrie.size[1]):
      pixel = entrie.getpixel((x, y))
      pixel = binarize(pixel)
      output.putpixel((x, y), pixel)
  return output

def r1Filter(entrie: Image.Image):
  CHECK1 = [5, 6, 7, 8, 9, 12]
  CHECK2 = [10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
  def r1Filter(entrie: list):
    res1, res2 = True, False
    for i in range(25):
      if i in CHECK1: res1 = (res1 and bool(entrie[i] == BLACK))
      elif i in CHECK2: res2 = (res2 or bool(entrie[i] == WHITE))
    return (res1 and res2)
  output = entrie.copy()
  lista = []
  for x in range(entrie.size[0] - 4):
    for y in range(entrie.size[1] - 4):
      for i in range(5):
        for j in range(5):
          lista.append(entrie.getpixel((x + i, y + j)))
      if r1Filter(lista):
        output.putpixel((x + 2, y + 2), WHITE)
      lista.clear()
  return output

def r2Filter(entrie: Image.Image):
  CHECK1 = [3, 7, 8, 13, 17, 18, 23]
  CHECK2 = [1, 6, 11, 16, 21]
  def r2Filter(entrie: list):
    res1, res2 = True, False
    for i in range(25):
      if i in CHECK1: res1 = (res1 and bool(entrie[i] == BLACK))
      elif i in CHECK2: res2 = (res2 or bool(entrie[i] == WHITE))
    return (res1 and res2)
  output = entrie.copy()
  lista = []
  for x in range(entrie.size[0] - 4):
    for y in range(entrie.size[1] - 4):
      for i in range(5):
        for j in range(5):
          lista.append(entrie.getpixel((x + i, y + j)))
      if r2Filter(lista):
        output.putpixel((x + 2, y + 2), WHITE)
      lista.clear()
  return output

def fillContour(entrie: cv.Mat):
  thresh = cv.threshold(entrie, 128, 255, cv.THRESH_BINARY)[1]
  KERNEL = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
  thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, KERNEL)
  return cv.cvtColor(np.zeros_like(thresh), cv.COLOR_RGB2BGR)

def boxBlur(entrie: Image.Image, radius = 3):
  FILTER = ImageFilter.BoxBlur(radius)
  return entrie.filter(FILTER)

def sobelFilter(entrie: cv.Mat) -> cv.Mat:
  xsobel = cv.Sobel(entrie, cv.CV_16S, 1, 0, ksize = 3, scale = 1)
  ysobel = cv.Sobel(entrie, cv.CV_16S, 0, 1, ksize = 3, scale = 1)
  xsobel = cv.convertScaleAbs(xsobel)
  ysobel = cv.convertScaleAbs(ysobel)
  return cv.addWeighted(xsobel, .5, ysobel, .5, 0)

def biggerContour(entrie: cv.Mat):
  canny = cannyFilter(entrie)
  contours, hierarchy = cv.findContours(canny, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
  with open("temp.txt", "w") as temp: temp.write(f"{contours}")
  entrieCopy = gray2bgr(entrie)
  cv.drawContours(entrieCopy, contours, -1, (0, 255, 0), 2)
  return entrieCopy

def binarize(entrie: cv.Mat, llevel: uint8 = 40):
  def binarize(entrie: uint8):
    if entrie < llevel: return WHITE
    return BLACK
  output = entrie.copy()
  for tupla in getTuplas(entrie.shape):
    output[tupla] = binarize(output[tupla])
  return output