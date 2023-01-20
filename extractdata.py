import cv2 as cv
from os import mkdir
from os.path import isfile, isdir
from numpy import full, uint8
from itertools import product
from threading import Thread
from sys import stderr

BLACK, WHITE, RED = 0, 255, (0, 0, 255)
LisTuple = list[tuple[int, int]]
LisLisTuple = list[LisTuple]

def bgr2gray(entrie: cv.Mat):
  return cv.cvtColor(entrie, cv.COLOR_BGR2GRAY)

def gray2bgr(entrie: cv.Mat):
  return cv.cvtColor(entrie, cv.COLOR_GRAY2BGR)

def openImage(entrie: str):
  if not isfile(entrie):
    print(f"\"{entrie}\" inexistente!"); exit()
  names = entrie.split(".")
  name, exten = names[0], names[1]
  temp = cv.imread(entrie)
  if exten != "png":
    cv.imwrite(f"{name}/{name}.png", temp)
  return name, bgr2gray(temp)

def cutImage(entrie: cv.Mat):
  cutted = entrie.copy()
  altura, largura = entrie.shape
  x1 = int(altura * 0.075)
  x2 = int(altura * 0.908)
  y1 = int(largura * 0.044)
  y2 = int(largura * 0.964)
  cutted = cutted[x1:x2, y1:y2]
  cutted = cv.resize(cutted, (4760, 1820))
  print("cutImage terminado!")
  return cutted

def claheFilter(entrie: cv.Mat):
  a, b, c = cv.split(gray2bgr(entrie))
  a = cv.createCLAHE(15, (8, 8)).apply(a)
  output = bgr2gray(cv.merge((a, b, c)))
  print("claheFilter terminado!")
  return output

def cannyFilter(entrie: cv.Mat) -> cv.Mat:
  output = cv.Canny(entrie, 200, 255, L2gradient = True)
  print("cannyFilter terminado!")
  return output

def estimateBack(entrie: cv.Mat, proc = 15):
  deleted = entrie.copy()
  estimated = full(entrie.shape, BLACK, uint8)
  listmp: LisLisTuple = []
  for x in range(entrie.shape[0]):
    temp = product([x], range(entrie.shape[1]))
    temp = [a for a in temp if entrie[a] == WHITE]
    listmp.append(temp)
  indexes: list[int] = []
  atual, lentmp = 0, len(listmp)
  while True:
    meio = lentmp
    for i in range(atual, lentmp):
      if len(listmp[i]) > 1200:
        meio = i; break
    if meio == lentmp: break
    raio = meio - proc
    for i in range(raio, meio):
      e1 = len(listmp[i])
      e2 = len(listmp[i+1])
      if (e2 - e1) > 100:
        pos1 = i; break
    raio = meio + proc
    for i in range(raio, meio, -1):
      e1 = len(listmp[i])
      e2 = len(listmp[i-1])
      if (e2 - e1) > 100:
        pos2 = i; break
    deleted[pos1:pos2, :] = BLACK
    pos2 += 1; atual = raio
    indexes.extend(range(pos1, pos2))
  for x in indexes:
    for elem in listmp[x]:
      estimated[elem] = WHITE
  print("estimateBack terminado!")
  return deleted, estimated

def xFilter2(entrie: cv.Mat, dist = 20):
  output = entrie.copy()
  lentrie = output.shape[0] - dist
  def xFilter2(y: int):
    pos1, flag = 0, True
    while True:
      flag = False
      for x in range(pos1, lentrie):
        if output[x, y] == WHITE:
          pos1, flag = x, True
          break
      if not flag: return
      pos2 = pos1 + dist
      for x in range(pos2, pos1, -1):
        if output[x, y] == WHITE:
          pos2 = x + 1
          for l in range(pos1, pos2):
            output[l, y] = BLACK
          temp = (pos1 + x)//2
          output[temp, y] = WHITE
          break
      pos1 = pos2
  colunas = range(output.shape[1])
  for y in colunas: xFilter2(y)
  print("xFilter2 terminado!")
  return output

def extractPixels(entrie: cv.Mat):
  altura, largura = entrie.shape
  temp = product(range(altura), range(largura))
  temp = sorted([x for x in temp if entrie[x] == WHITE])
  print("extractPixels terminado!")
  return temp

def juntarImgs(entrie: cv.Mat, listas: LisTuple):
  output = entrie.copy()
  for tupla in listas: output[tupla] = WHITE
  print("juntarImgs terminado!")
  return output

def organizePixels(tuplas: LisTuple, shape:
        tuple[int, int], dname: str, x: int, radius = 10):
  listas: LisLisTuple = []
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
  listas = organizeData(listas)
  listas = [elem for elem in listas if len(elem) > 500]
  preta = full(shape, BLACK, uint8)
  if not isdir(f"{dname}/img"): mkdir(f"{dname}/img")
  for i, sublista in enumerate(listas):
    imagem = preta.copy()
    with open(f"{dname}/img/{x}{i}.txt", "w") as saida:
      saida.write(f"Tam.: {shape}\n")
      for tupla in sublista:
        saida.write(f"{tupla}\n")
        imagem[tupla] = WHITE
    cv.imwrite(f"{dname}/img/{x}{i}.png", imagem)
  print("organizePixels terminado!")
  return listas

def organizeData(entrie: LisLisTuple, d = 10, t = 60):
  listemp1: LisLisTuple = []
  for sublista in entrie:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      if tupla[1] != temp[-1][1]:
        temp.append(tupla)
    listemp1.append(temp)
  listemp2: LisLisTuple = []
  for sublista in listemp1:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      e1 = tupla[1]
      e2 = temp[-1][1]
      if (e1 - e2) > d and len(temp) < t:
        temp.clear()
      temp.append(tupla)
    listemp2.append(temp)
  listemp3: LisLisTuple = []
  for sublista in listemp2:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      e1 = tupla[0]
      e2 = temp[-1][0]
      if -d <= (e1 - e2) <= d:
        temp.append(tupla)
    listemp3.append(temp)
  return listemp3

def calcDiff(dname: str, entrie1: LisLisTuple, entrie2: LisLisTuple):
  if not isdir(f"{dname}/list"): mkdir(f"{dname}/list")
  for i, sublist1 in enumerate(entrie1):
    for j, sublist2 in enumerate(entrie2):
      with open(f"{dname}/list/{i}{j}.txt", "w") as saida:
        for elem1, elem2 in product(sublist1, sublist2):
          if elem1[1] == elem2[1]:
            dist = abs(elem1[0] - elem2[0])
            saida.write(f"{elem1}{elem2} - {dist}\n")
  print("calcDiff terminado!")

def sobrepor(canny: cv.Mat, listas: LisLisTuple):
  output = gray2bgr(canny)
  for sublista in listas:
    for tupla in sublista:
      output[tupla] = RED
  print("sobrepor terminado!")
  return output

class rThread(Thread):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._result = None
  
  def run(self):
    if self._target is None:
      raise RuntimeError("Target não especificado!")
    try: self._result = self._target(*self._args, **self._kwargs)
    except Exception as exc:
      print(f"{type(exc).__name__}: {exc}", file = stderr)
  
  def join(self, *args, **kwargs):
    super().join(*args, **kwargs)
    return self._result