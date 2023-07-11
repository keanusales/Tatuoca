from numpy import full, ndenumerate
from os.path import isfile, isdir
from itertools import product
from os import mkdir, system
import cv2 as cv

BLACK, WHITE, RED = 0, 255, (0, 0, 255)
tuple2int = tuple[int, int]
listTuple = list[tuple2int]
listsTuple = list[listTuple]
shape = (1820, 4760)

def bgr2gray(entrie: cv.Mat):
  return cv.cvtColor(entrie, cv.COLOR_BGR2GRAY)

def gray2bgr(entrie: cv.Mat):
  return cv.cvtColor(entrie, cv.COLOR_GRAY2BGR)

def openImage(entrie: str):
  if not isfile(entrie):
    exit(f"\"{entrie}\" inexistente!")
  name, exten = entrie.split(".")
  temp = cv.imread(entrie)
  if exten != "png":
    cv.imwrite(f"{name}/{name}.png", temp)
  return name, bgr2gray(temp)

def cutImage(entrie: cv.Mat, fator = 10):
  ALTR, LARG = entrie.shape
  tamanho = (LARG//fator, ALTR//fator)
  res = cv.resize(entrie, tamanho)
  res = cv.adaptiveThreshold(res, 255,
    cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 9, 9)
  res = cannyFilter(res)
  res = estimateBack(res, 380, 10)[1]
  res = xFilter2(res, 10)
  res = organize(extract(res), 5, 350)
  res.sort(key = lambda x: x[0][0])
  altr, larg = res[0][len(res[0])//2]
  altr, larg = altr*fator, larg*fator
  x1 = altr - round((124/267)*ALTR)
  x2 = altr + round((197/534)*ALTR)
  y1 = larg - round((589/1250)*LARG)
  y2 = larg + round((561/1250)*LARG)
  cutted = entrie[x1:x2, y1:y2]
  cutted = cv.resize(cutted, (4760, 1820))
  print("cutImage terminado!")
  return cutted

def gaussThresh(entrie: cv.Mat) -> cv.Mat:
  output = cv.adaptiveThreshold(entrie, 255,
    cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 17, 10)
  output = cv.GaussianBlur(output, (11, 11), 0)
  print("gaussThresh terminado!")
  return output

def cannyFilter(entrie: cv.Mat) -> cv.Mat:
  output = cv.Canny(entrie, 200, 255, L2gradient = True)
  print("cannyFilter terminado!")
  return output

def estimateBack(entrie: cv.Mat, quant = 1200, proc = 15):
  deleted = entrie.copy()
  estimated = full(entrie.shape, BLACK, "u1")
  listmp = [[(i1, i2) for i2, elem in enumerate(arr) if elem]
            for i1, arr in enumerate(entrie == WHITE)]
  indexes: list[int] = []
  atual, lentmp = 0, len(listmp)
  while True:
    meio = lentmp
    for i in range(atual, lentmp):
      if len(listmp[i]) > quant:
        meio = i; break
    if meio == lentmp: break
    raio = meio - proc
    for i in range(raio, meio):
      e1 = len(listmp[i])
      e2 = len(listmp[i+1])
      if (e2 - e1) > (quant//12):
        pos1 = i; break
    raio = meio + proc
    for i in range(raio, meio, -1):
      e1 = len(listmp[i])
      e2 = len(listmp[i-1])
      if (e2 - e1) > (quant//12):
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
  linhas, colunas = output.shape
  lentrie = linhas - dist
  for y in range(colunas):
    pos1, flag = 0, True
    while True:
      flag = False
      for a in range(pos1, lentrie):
        if output[a, y] == WHITE:
          pos1, flag = a, True
          break
      if not flag: break
      pos2 = pos1 + dist
      for b in range(pos2, pos1, -1):
        if output[b, y] == WHITE:
          pos2 = b + 1
          break
      output[pos1:pos2, y] = BLACK
      temp, pos1 = (a + b)//2, pos2
      output[temp, y] = WHITE
  print("xFilter2 terminado!")
  return output

def extract(entrie: cv.Mat):
  elems = ndenumerate(entrie == WHITE)
  output = [idx for idx, elem in elems if elem]
  output.sort(); print("extract terminado!")
  return output

def juntarImgs(listas: listsTuple):
  output = full(shape, BLACK, "u1")
  dim1, dim2 = zip(*(elem for sub in listas for elem in sub))
  output[dim1, dim2] = WHITE; print("juntarImgs terminado!")
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
  print("organize terminado!")
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
    cv.imwrite(f"{pasta}/{dtype}{i}.png", imagem)
  print("saveLists terminado!")

def calcDiff(dname: str, curves: listsTuple, basels: listsTuple):
  pasta = f"{dname}/calculoDiff"
  if not isdir(pasta): mkdir(pasta)
  ncurves, nbasels = enumerate(curves), enumerate(basels)
  for (a, sub1), (b, sub2) in product(ncurves, nbasels):
    with open(f"{pasta}/curve{a}base{b}.txt", "w") as saida:
      pos2, len2 = 0, len(sub2)
      for el1 in sub1:
        e1, e2 = el1
        for i in range(pos2, len2):
          e3, e4 = el2 = sub2[i]
          if e2 == e4:
            pos2, dis = (i + 1), abs(e1 - e3)
            saida.write(f"{el1}{el2} - {dis}\n")
            break
  print("calcDiff terminado!")

def sobrepor(canny: cv.Mat, listas: listsTuple):
  output = gray2bgr(canny)
  dim1, dim2 = zip(*(elem for sub in listas for elem in sub))
  output[dim1, dim2] = RED; print("sobrepor terminado!")
  return output

if __name__ == "__main__":
  system("cls||clear")
  name, output = openImage(input("Entrie archive: "))
  if not isdir(name): mkdir(name)

  output = cutImage(output)
  cv.imwrite(f"{name}/cutted.png", output)
  output = gaussThresh(output)
  cv.imwrite(f"{name}/gauss.png", output)
  canny = cannyFilter(output)
  cv.imwrite(f"{name}/canny.png", canny)

  deleted, estimat = estimateBack(canny)
  cv.imwrite(f"{name}/estimat.png", estimat)
  cv.imwrite(f"{name}/deleted.png", deleted)

  deleted, estimat = xFilter2(deleted), xFilter2(estimat)
  cv.imwrite(f"{name}/filter1.png", deleted)
  cv.imwrite(f"{name}/filter2.png", estimat)

  lista1, lista2 = extract(deleted), extract(estimat)
  output = juntarImgs([lista1, lista2])
  cv.imwrite(f"{name}/juntos.png", output)

  lista1, lista2 = organize(lista1), organize(lista2)
  saveLists(lista1, "curve", name)
  saveLists(lista2, "base", name)
  calcDiff(name, lista1, lista2)

  saida1 = sobrepor(output, lista1)
  saida2 = sobrepor(canny, lista1)
  cv.imwrite(f"{name}/sobre1.png", saida1)
  cv.imwrite(f"{name}/sobre2.png", saida2)

  print("Processo Terminado!")