import cv2 as cv
from numpy import full, uint8
from itertools import product
from os.path import isfile
from os import system

BLACK, WHITE, RED = 0, 255, (0, 0, 255)

def bgr2gray(entrie: cv.Mat):
  return cv.cvtColor(entrie, cv.COLOR_BGR2GRAY)

def gray2bgr(entrie: cv.Mat):
  return cv.cvtColor(entrie, cv.COLOR_GRAY2BGR)

def openImage(entrie: str, convert = True):
  if not isfile(entrie):
    print(f"\"{entrie}\" inexistente!"); exit(0)
  temp = cv.imread(entrie)
  return bgr2gray(temp) if convert else temp

def saveImage(fname: str, entrie: cv.Mat, convert = True):
  temp = gray2bgr(entrie) if convert else entrie
  return cv.imwrite(fname, temp)

def getTuplas(entrie: cv.Mat.shape):
  return product(range(entrie[0]), range(entrie[1]))

def claheFilter(entrie: cv.Mat):
  a, b, c = cv.split(gray2bgr(entrie))
  a = cv.createCLAHE(15, (8, 8)).apply(a)
  return bgr2gray(cv.merge((a, b, c)))

def bilateral(entrie: cv.Mat, key = 7) -> cv.Mat:
  return cv.bilateralFilter(entrie, key, 75, 75)

def cannyFilter(entrie: cv.Mat) -> cv.Mat:
  return cv.Canny(entrie, 50, 250, L2gradient = True)

def xFilter(entrie: cv.Mat, length = 10):
  output = entrie.copy()
  def xFilter(pair1: int, pair2: int):
    def xFilter(cord1: int, cord2: int):
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
      if xFilter(cord1, cord2): break
      cord1 += 1
      if xFilter(cord1, cord2): break
      cord1 -= 1; cord2 -= 1
      if xFilter(cord1, cord2): break
      cord1 += 1
  altura, largura = output.shape
  atr1, atr2 = length + 1, altura - length
  tuplas = product(range(atr1, atr2), range(largura))
  for x, y in tuplas: xFilter(x, y)
  return output

def organizeData(entrie: list, dist = 10, tam = 30):
  templist1 = []
  for sublista in entrie:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      if tupla[1] == temp[-1][1]:
        del temp[-1]
      temp.append(tupla)
    templist1.append(temp)
  templist2 = []
  for sublista in templist1:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      y1 = tupla[1]
      y2 = temp[-1][1]
      if (y1 - y2) > dist and len(temp) < tam:
        temp.clear()
      temp.append(tupla)
    templist2.append(temp)
  return templist2

def extract(entrie: cv.Mat, fname: str, radius = 5):
  tuplas = getTuplas(entrie.shape)
  tuplas = [x for x in tuplas if entrie[x] == WHITE]
  tuplas = sorted(tuplas)
  with open(f"{fname}.tup.txt", "w") as saida:
    for tupla in tuplas: saida.write(f"{tupla}\n")
  listas: list[list[tuple[int, int]]] = []
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
  preta = full(entrie.shape, BLACK, uint8)
  sobre = gray2bgr(entrie)
  for i in range(3):
    imagem = preta.copy()
    with open(f"{fname}{i}.txt", "w") as saida:
      saida.write(f"Tam. img.: {entrie.shape}\n")
      for tupla in listas[i]:
        saida.write(f"{tupla}\n")
        imagem[tupla] = WHITE
        sobre[tupla] = RED
    saveImage(f"{fname}{i}.png", imagem)
  return sobre

def sobrepor(canny: cv.Mat, aux: cv.Mat):
  convert = gray2bgr(canny)
  for tupla in getTuplas(aux.shape):
    if tuple(aux[tupla]) == RED:
      convert[tupla] = RED
  return convert

if __name__ == "__main__":
  system("cls||clear")
  entrie = input("Entrie archive: ")
  opened = openImage(entrie)
  name = entrie[:entrie.index(".")]
  output = claheFilter(opened)
  saveImage(f"{name}.clahe.png", output)
  output = bilateral(output)
  saveImage(f"{name}.bilat.png", output)
  canny = cannyFilter(output)
  saveImage(f"{name}.canny.png", canny)
  output = xFilter(canny)
  saveImage(f"{name}.filter.png", output)
  saida = extract(output, name)
  output = sobrepor(output, saida)
  saveImage(f"{name}.sobre1.png", output, 0)
  output = sobrepor(canny, saida)
  saveImage(f"{name}.sobre2.png", output, 0)