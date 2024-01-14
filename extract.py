from os.path import isfile, isdir
from cv2.typing import MatLike
from itertools import groupby
from numpy import full
from os import mkdir
from cv2 import (
  imread, imwrite, cvtColor,
  adaptiveThreshold, Canny,
  GaussianBlur, resize,
  ADAPTIVE_THRESH_GAUSSIAN_C,
  COLOR_BGR2GRAY,
  COLOR_GRAY2BGR,
  THRESH_BINARY
)

BLACK, WHITE, RED = 0, 255, (0, 0, 255)
tuple2int = tuple[int, int]
listTuple = list[tuple2int]
listsTuple = list[listTuple]
shape = (1800, 4590)

def bgr2gray(entrie: MatLike):
  return cvtColor(entrie, COLOR_BGR2GRAY)

def gray2bgr(entrie: MatLike):
  return cvtColor(entrie, COLOR_GRAY2BGR)

def imopen(entrie: str):
  if not isfile(entrie):
    exit(f"\"{entrie}\" inexistente!")
  name, _ = entrie.split(".")
  image = imread(entrie)
  return name, bgr2gray(image)

def cutImage(entrie: MatLike, fator = 10):
  ALTR, LARG = entrie.shape
  tamanho = (LARG//fator, ALTR//fator)
  res = resize(entrie, tamanho)
  res = gaussThresh(res, 9, 9)
  res = cannyFilter(res)
  res = separeLines(res, 380, 10)[1]
  res = skeletonize(res, 10)
  res = organize(extractWhites(res), 5, 350)
  res.sort(key = lambda x: x[0][0])
  altr, larg = res[0][len(res[0])//2]
  altr, larg = altr*fator, larg*fator
  x1 = altr - round((124/267)*ALTR)
  x2 = altr + round((197/534)*ALTR)
  y1 = larg - round((589/1250)*LARG)
  y2 = larg + round((561/1250)*LARG)
  cutted = entrie[x1:x2, y1:y2]
  cutted = resize(cutted, shape[::-1])
  print("cutImage terminado!")
  return cutted

def gaussThresh(entrie: MatLike, size = 19, C = 10):
  output = adaptiveThreshold(entrie, 255,
    ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, size, C)
  print("gaussThresh terminado!")
  return output

def gaussBlur(entrie: MatLike):
  output = GaussianBlur(entrie, (11, 11), 0)
  print("gaussThresh terminado!")
  return output

def cannyFilter(entrie: MatLike):
  output = Canny(entrie, 200, 255, L2gradient = True)
  print("cannyFilter terminado!")
  return output

def extractWhites(entrie: MatLike):
  output = [*zip(*(entrie == WHITE).nonzero())]
  print("extractWhites terminado!")
  return output

def separeLines(entrie: MatLike, quant = 1200, proc = 15):
  original_copy = entrie.copy()
  background = full(entrie.shape, BLACK, "u1")
  whites = (entrie == WHITE).sum(axis = 1)
  atual, lentmp = 0, len(whites)
  while True:
    meio = lentmp
    for i in range(atual, lentmp):
      if whites[i] > quant:
        meio = i; break
    if meio == lentmp: break
    raio = meio - proc
    for i in range(raio, meio):
      e1 = whites[i]
      e2 = whites[i+1]
      if (e2 - e1) > (quant//12):
        pos1 = i; break
    raio = meio + proc
    for i in range(raio, meio, -1):
      e1 = whites[i]
      e2 = whites[i-1]
      if (e2 - e1) > (quant//12):
        pos2 = i; break
    background[pos1:pos2] = original_copy[pos1:pos2]
    original_copy[pos1:pos2], atual = BLACK, raio
  print("estimateBack terminado!")
  return original_copy, background

def skeletonize(entrie: MatLike, distance = 20):
  original_copy = entrie.copy()
  transpose = original_copy.T
  whites = extractWhites(transpose)
  whites = groupby(whites, lambda x: x[0])
  for key, listas in whites:
    point1 = point2 = 0
    listas = [*listas]
    lenlistas = len(listas)
    while True:
      (a, y0) = (a, y1) = listas[point1]
      for pos in range(point1 + 1, lenlistas):
        (a, ny), point2 = listas[pos], pos
        if (ny - y0) > distance: break
        (a, y1) = (a, ny)
      if point1 == point2: break
      transpose[key, y0:(y1 + 1)] = BLACK
      midpoint = ((y0 + y1) // 2)
      transpose[key, midpoint] = WHITE
      point1 = point2
  print("skeletonize terminado!")
  return original_copy

def juntarImgs(listas: listsTuple):
  output = full(shape, BLACK, "u1")
  output[*zip(*(e for s in listas for e in s))] = WHITE
  print("juntarImgs terminado!")
  return output

def sobrepor(canny: MatLike, listas: listsTuple):
  output = gray2bgr(canny)
  output[*zip(*(e for s in listas for e in s))] = RED
  print("sobrepor terminado!")
  return output

def organize(tuplas: listTuple, radius = 10, minlen = 1200):
  DIST, TAM = 10, 60
  listas: listsTuple = []
  pos1 = 0; lentup = len(tuplas)
  while pos1 != lentup:
    temp = [tuplas[pos1]]
    pos1 += 1; pos2 = lentup
    for i in range(pos1, lentup):
      x1 = tuplas[i][0]
      x2 = temp[-1][0]
      if (x1 - x2) > radius:
        pos2 = i; break
      temp.append(tuplas[i])
    listas.append(temp)
    pos1 = pos2
  listas.sort(key = lambda x: len(x), reverse = True)
  for elem in listas: elem.sort(key = lambda x: x[1])
  list1: listsTuple = []
  for sublista in listas:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      res1 = tupla[1] - temp[-1][1]
      if res1 > DIST and len(temp) < TAM:
        temp.clear()
      temp.append(tupla)
    list1.append(temp)
  list2: listsTuple = []
  for sublista in list1:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      res1 = tupla[0] - temp[-1][0]
      res2 = tupla[1] != temp[-1][1]
      if abs(res1) <= DIST and res2:
        temp.append(tupla)
    list2.append(temp)
  listas = [elem for elem in list2 if len(elem) > minlen]
  listas.sort(); print("organize terminado!")
  return listas

def saveLists(listas: listsTuple, dtype: str, dname: str):
  preta = full(shape, BLACK, "u1")
  pasta = f"{dname}/processImg"
  if not isdir(pasta): mkdir(pasta)
  for i, sublista in enumerate(listas):
    imagem = preta.copy()
    with open(f"{pasta}/{dtype}{i}.txt", "w") as saida:
      saida.write(f"Tam.: {shape}\n")
      for tupla in sublista:
        saida.write(f"{tupla}\n")
        imagem[tupla] = WHITE
    imwrite(f"{pasta}/{dtype}{i}.png", imagem)
  print("saveLists terminado!")