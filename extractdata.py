from numpy import full, ndenumerate
from os.path import isfile, isdir
from os import mkdir
from cv2 import (
  Mat, imread, imwrite,
  cvtColor, adaptiveThreshold,
  Canny, GaussianBlur, resize,
  ADAPTIVE_THRESH_GAUSSIAN_C,
  COLOR_BGR2GRAY,
  COLOR_GRAY2BGR,
  THRESH_BINARY
)

BLACK, WHITE, RED = 0, 255, (0, 0, 255)
tuple2int = tuple[int, int]
listTuple = list[tuple2int]
listsTuple = list[listTuple]
shape = (1820, 4760)

def bgr2gray(entrie: Mat):
  return cvtColor(entrie, COLOR_BGR2GRAY)

def gray2bgr(entrie: Mat):
  return cvtColor(entrie, COLOR_GRAY2BGR)

def imopen(entrie: str):
  if not isfile(entrie):
    exit(f"\"{entrie}\" inexistente!")
  name, exten = entrie.split(".")
  temp = imread(entrie)
  if exten != "png":
    imwrite(f"{name}/{name}.png", temp)
  return name, bgr2gray(temp)

def cutImage(entrie: Mat, fator = 10):
  ALTR, LARG = entrie.shape
  tamanho = (LARG//fator, ALTR//fator)
  res = resize(entrie, tamanho)
  res = gaussThresh(res, 9, 9)
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
  cutted = resize(cutted, shape[::-1])
  print("cutImage terminado!")
  return cutted

def gaussThresh(entrie: Mat, size = 19, C = 10) -> Mat:
  output = adaptiveThreshold(entrie, 255,
    ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, size, C)
  print("gaussThresh terminado!")
  return output

def gaussBlur(entrie: Mat) -> Mat:
  output = GaussianBlur(entrie, (11, 11), 0)
  print("gaussThresh terminado!")
  return output

def cannyFilter(entrie: Mat) -> Mat:
  output = Canny(entrie, 200, 255, L2gradient = True)
  print("cannyFilter terminado!")
  return output

def estimateBack(entrie: Mat, quant = 1200, proc = 15):
  deleted = entrie.copy()
  estimated = full(entrie.shape, BLACK, "u1")
  lista = [[(i1, i2) for i2, elem in enumerate(arr) if elem]
            for i1, arr in enumerate(entrie == WHITE)]
  index: list[int] = []
  atual, lentmp = 0, len(lista)
  while True:
    meio = lentmp
    for i in range(atual, lentmp):
      if len(lista[i]) > quant:
        meio = i; break
    if meio == lentmp: break
    raio = meio - proc
    for i in range(raio, meio):
      e1 = len(lista[i])
      e2 = len(lista[i+1])
      if (e2 - e1) > (quant//12):
        pos1 = i; break
    raio = meio + proc
    for i in range(raio, meio, -1):
      e1 = len(lista[i])
      e2 = len(lista[i-1])
      if (e2 - e1) > (quant//12):
        pos2 = i; break
    deleted[pos1:pos2, :] = BLACK
    pos2 += 1; atual = raio
    index.extend(range(pos1, pos2))
  dim1, dim2 = zip(*(e for x in index for e in lista[x]))
  estimated[dim1, dim2] = WHITE
  print("estimateBack terminado!")
  return deleted, estimated

def xFilter2(entrie: Mat, dist = 20):
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

def extract(entrie: Mat):
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

def sobrepor(canny: Mat, listas: listsTuple):
  output = gray2bgr(canny)
  dim1, dim2 = zip(*(elem for sub in listas for elem in sub))
  output[dim1, dim2] = RED; print("sobrepor terminado!")
  return output