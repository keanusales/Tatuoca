import cv2 as cv
from os import mkdir
from numpy import full, uint8
from itertools import product
from os.path import isfile, isdir
from threading import Thread
from sys import stderr

BLACK, WHITE, RED = 0, 255, (0, 0, 255)
ListsTuple = list[list[tuple[int, int]]]

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
  cutted = cv.resize(cutted, (2380, 910))
  print("cutImage terminado!")
  return cutted

def getTupShape(entrie: cv.Mat.shape):
  return product(range(entrie[0]), range(entrie[1]))

def claheFilter(entrie: cv.Mat):
  a, b, c = cv.split(gray2bgr(entrie))
  a = cv.createCLAHE(15, (8, 8)).apply(a)
  output = bgr2gray(cv.merge((a, b, c)))
  print("claheFilter terminado!")
  return output

def bilateral(entrie: cv.Mat, key = 7) -> cv.Mat:
  output = cv.bilateralFilter(entrie, key, 75, 75)
  print("bilateral terminado!")
  return output

def cannyFilter(entrie: cv.Mat) -> cv.Mat:
  output = cv.Canny(entrie, 220, 255, L2gradient = True)
  print("cannyFilter terminado!")
  return output

def estimateBack(entrie: cv.Mat, proc = 1, est = 3):
  deleted = entrie.copy()
  estimated = full(entrie.shape, BLACK, uint8)
  listemp: ListsTuple = []
  for x in range(1, entrie.shape[0] - 1):
    temp = range(x - proc, x + proc + 1)
    temp = product(temp, range(entrie.shape[1]))
    temp = [tupla for tupla in temp if entrie[tupla] == WHITE]
    listemp.append(temp)
  indexes: list[int] = []
  for x, temp in enumerate(listemp):
    if len(temp) > 1800:
      x1, x2 = x - est, x + est
      indexes.extend(range(x1, x2+1))
      deleted[x1:x2, :] = BLACK
  for x in indexes:
    for elem in listemp[x]: estimated[elem] = WHITE
  print("estimateBack terminado!")
  return deleted, estimated

def xFilter(entrie: cv.Mat, length = 5):
  output = entrie.copy()
  def funcao1(pair1: int, pair2: int):
    def funcao2(cord1: int, cord2: int):
      pixel1 = output[cord1, pair2]
      pixel2 = output[cord2, pair2]
      if pixel1 == pixel2 == WHITE:
        for x in range(cord1, cord2 + 1):
          output[x, pair2] = BLACK
        output[pair1, pair2] = WHITE
        return True
      return False
    cord1 = pair1 - length
    cord2 = pair1 + length
    while cord1 != cord2:
      if funcao2(cord1, cord2): break
      cord1 += 1
      if funcao2(cord1, cord2): break
      cord1 -= 1; cord2 -= 1
      if funcao2(cord1, cord2): break
      cord1 += 1
  altura, largura = output.shape
  atr1, atr2 = length + 1, altura - length
  tuplas = product(range(atr1, atr2), range(largura))
  for x, y in tuplas: funcao1(x, y)
  print("xFilter terminado!")
  return output

def extract(entrie: cv.Mat, dname: str, x: int, radius = 5):
  tuplas = getTupShape(entrie.shape)
  tuplas = [x for x in tuplas if entrie[x] == WHITE]
  tuplas = sorted(tuplas)
  with open(f"{dname}/tup.txt", "w") as saida:
    for tupla in tuplas: saida.write(f"{tupla}\n")
  listas: ListsTuple = []
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
  preta = full(entrie.shape, BLACK, uint8)
  sobre = gray2bgr(entrie)
  if not isdir(f"{dname}/img"): mkdir(f"{dname}/img")
  for i, sublista in enumerate(listas):
    imagem = preta.copy()
    with open(f"{dname}/img/{x}{i}.txt", "w") as saida:
      saida.write(f"Tam.: {entrie.shape}\n")
      for tupla in sublista:
        saida.write(f"{tupla}\n")
        imagem[tupla] = WHITE
        sobre[tupla] = RED
    cv.imwrite(f"{dname}/img/{x}{i}.png", imagem)
  print("extract terminado!")
  return sobre, listas

def writeArch(dname: str, entrie1: ListsTuple, entrie2: ListsTuple):
  if not isdir(f"{dname}/list"): mkdir(f"{dname}/list")
  for i, sublist1 in enumerate(entrie1):
    for j, sublist2 in enumerate(entrie2):
      with open(f"{dname}/list/{i}{j}.txt", "w") as saida:
        for elem1, elem2 in product(sublist1, sublist2):
          if elem1[1] == elem2[1]:
            dist = abs(elem1[0] - elem2[0])
            saida.write(f"{elem1}{elem2} - {dist}\n")
  print("writeArch terminado!")

def organizeData(entrie: ListsTuple, d = 5, t = 30):
  listemp1: ListsTuple = []
  for sublista in entrie:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      if tupla[1] != temp[-1][1]:
        temp.append(tupla)
    listemp1.append(temp)
  listemp2: ListsTuple = []
  for sublista in listemp1:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      e1 = tupla[1]
      e2 = temp[-1][1]
      if (e1 - e2) > d and len(temp) < t:
        temp.clear()
      temp.append(tupla)
    listemp2.append(temp)
  listemp3: ListsTuple = []
  for sublista in listemp2:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      e1 = tupla[0]
      e2 = temp[-1][0]
      if -d <= (e1 - e2) <= d:
        temp.append(tupla)
    listemp3.append(temp)
  return listemp3

def juntarImgs(entrie: cv.Mat, aux: cv.Mat):
  output = entrie.copy()
  for tupla in getTupShape(entrie.shape):
    if aux[tupla] == WHITE:
      output[tupla] = WHITE
  print("juntarImgs terminado!")
  return output

def sobrepor(canny: cv.Mat, aux: cv.Mat):
  output = gray2bgr(canny)
  for tupla in getTupShape(aux.shape):
    if tuple(aux[tupla]) == RED:
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