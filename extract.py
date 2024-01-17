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
  name, a = entrie.split(".")
  image = imread(entrie)
  return name, bgr2gray(image)

def cutImage(entrie: MatLike, fator = 10):
  ALTR, LARG = entrie.shape
  tamanho = (LARG//fator, ALTR//fator)
  res = resize(entrie, tamanho)
  res = gaussThresh(res, 9, 9)
  res = cannyFilter(res)
  a, res = separeLines(res, 380, 10)
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

def separeLines(entrie: MatLike, quant = 1200, proc = 15):
  original_copy = entrie.copy()
  background = full(entrie.shape, BLACK, "u1")
  quants = (entrie == WHITE).sum(axis = 1)
  diffs1 = (quants[1:] - quants[:-1]) > (quant // 12)
  diffs2 = (quants[:-1] - quants[1:]) > (quant // 12)
  quants = (quants > quant)
  raio, lenquants = 0, len(quants)
  while True:
    atual, meio = raio, lenquants
    for i in range(atual, lenquants):
      if quants[i]: meio = i; break
    if meio == lenquants: break
    raio = meio - proc
    for i in range(raio, meio):
      if diffs1[i]: pos1 = (i - 2); break
    raio = meio + proc
    for i in range(raio, meio, -1):
      if diffs2[i-1]: pos2 = (i + 2); break
    background[pos1:pos2] = original_copy[pos1:pos2]
    original_copy[pos1:pos2] = BLACK
  print("estimateBack terminado!")
  return original_copy, background

def extractWhites(entrie: MatLike):
  output = [*zip(*(entrie == WHITE).nonzero())]
  print("extractWhites terminado!")
  return output

def skeletonize(entrie: MatLike, distance = 20):
  original_copy = entrie.copy()
  transpose = original_copy.T
  whites = extractWhites(transpose)
  whites = groupby(whites, lambda x: x[0])
  for line, elems in whites:
    point2, elems = 0, [*elems]
    lenelems = len(elems)
    while True:
      point1 = point2
      (a, y0) = (a, y1) = elems[point1]
      for pos in range(point1 + 1, lenelems):
        (a, ny), point2 = elems[pos], pos
        if (ny - y0) > distance: break
        (a, y1) = (a, ny)
      if point1 == point2: break
      transpose[line, y0:(y1 + 1)] = BLACK
      midpoint = ((y0 + y1) // 2)
      transpose[line, midpoint] = WHITE
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
  elems1: listsTuple = []
  pos1, lentup = 0, len(tuplas)
  while pos1 != lentup:
    temp = [tuplas[pos1]]
    pos1 += 1; pos2 = lentup
    for i in range(pos1, lentup):
      (x1, a), (x2, a) = tuplas[i], temp[-1]
      if (x1 - x2) > radius: pos2 = i; break
      temp.append(tuplas[i])
    elems1.append(temp)
    pos1 = pos2
  elems1.sort(key = lambda x: len(x), reverse = True)
  for elem in elems1: elem.sort(key = lambda x: x[1])
  elems2: listsTuple = []
  for sublista in elems1:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      (a, r1), (a, r2) = tupla, temp[-1]
      if (r1 - r2) > DIST and len(temp) < TAM:
        temp.clear()
      temp.append(tupla)
    elems2.append(temp)
  list2: listsTuple = []
  for sublista in elems2:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      (r1, r2), (r3, r4) = tupla, temp[-1]
      if abs(r1 - r3) <= DIST and (r2 != r4):
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
    imagem[*zip(*(elem for elem in sublista))] = WHITE
    imwrite(f"{pasta}/{dtype}{i}.png", imagem)
    with open(f"{pasta}/{dtype}{i}.txt", "w") as saida:
      saida.write(f"Tam.: {shape}\n")
      for tupla in sublista: saida.write(f"{tupla}\n")
  print("saveLists terminado!")