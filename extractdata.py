import cv2 as cv
from os import mkdir, system
from os.path import isfile, isdir
from numpy import (full, uint8,
  array, array_split as split)
from itertools import product
from threading import Thread
from sys import stderr

BLACK, WHITE, RED = 0, 255, (0, 0, 255)
tuple2int = tuple[int, int]
listTuple = list[tuple2int]
listsTuple = list[listTuple]

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

def cutImage(entrie: cv.Mat, fator = 10):
  ALTR, LARG = entrie.shape
  tamanho = (LARG//fator, ALTR//fator)
  res = cv.resize(entrie, tamanho)
  res = cannyFilter(claheFilter(res))
  res = estimateBack(res, 380, 10)[1]
  res = xFilter2(res, 10, 4)
  res = organize(extract(res, 4), 5, 350)
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

def estimateBack(entrie: cv.Mat, quant = 1200, proc = 15):
  deleted = entrie.copy()
  estimated = full(entrie.shape, BLACK, uint8)
  listmp: listsTuple = []
  for x in range(entrie.shape[0]):
    temp = product([x], range(entrie.shape[1]))
    temp = [a for a in temp if entrie[a] == WHITE]
    listmp.append(temp)
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

def xFilter2(entrie: cv.Mat, dist = 20, qThreads = 2):
  output = entrie.copy()
  lentrie = output.shape[0] - dist
  def subPart1(entrie: list[int]):
    def subPart2(y: int):
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
    for y in entrie: subPart2(y)
  colunas = output.shape[1]
  colunas = split(array(range(colunas)), qThreads)
  threads = [Thread(target = subPart1, args = [elem])
    for elem in [list(elem) for elem in colunas]]
  for thread in threads: thread.start()
  for thread in threads: thread.join()
  print("xFilter2 terminado!")
  return output

def extract(entrie: cv.Mat, qThreads = 2):
  altura = range(entrie.shape[0])
  def subPart(largura: list[int]):
    temp = product(altura, largura)
    return [x for x in temp if entrie[x] == WHITE]
  largura = range(entrie.shape[1])
  temp = split(array(largura), qThreads)
  threads = [rThread(target = subPart, args = [elem])
    for elem in [list(elem) for elem in temp]]
  for thread in threads: thread.start()
  output = [x for t in threads for x in t.join()]
  output = sorted(output)
  print("extract terminado!")
  return output

def juntarImgs(shape: tuple2int, listas: listsTuple):
  output = full(shape, BLACK, uint8)
  temp = [elem for sub in listas for elem in sub]
  for tupla in temp: output[tupla] = WHITE
  print("juntarImgs terminado!")
  return output

def organize(tuplas: listTuple, radius = 10, minlen = 1000):
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
  listas = suborganize(listas)
  listas = [elem for elem in listas if len(elem) > minlen]
  print("organize terminado!")
  return listas

def suborganize(entrie: listsTuple):
  DIST, TAM = 10, 60
  listemp1: listsTuple = []
  for sublista in entrie:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      res1 = tupla[0] - temp[-1][0]
      res2 = tupla[1] != temp[-1][1]
      if -DIST <= res1 <= DIST and res2:
        temp.append(tupla)
    listemp1.append(temp)
  listemp2: listsTuple = []
  for sublista in listemp1:
    temp = [sublista[0]]
    for tupla in sublista[1:]:
      res1 = tupla[1] - temp[-1][1]
      if res1 > DIST and len(temp) < TAM:
        temp.clear()
      temp.append(tupla)
    listemp2.append(temp)
  return listemp2

contcalls = 0
def saveLists(listas: listsTuple, shape: tuple2int, dname: str):
  global contcalls
  dtype = ["curve", "base"][contcalls]
  contcalls += 1
  preta = full(shape, BLACK, uint8)
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
  for i, sublist1 in enumerate(curves):
    for j, sublist2 in enumerate(basels):
      with open(f"{pasta}/curve{i}base{j}.txt", "w") as saida:
        for elem1, elem2 in product(sublist1, sublist2):
          if elem1[1] == elem2[1]:
            dist = abs(elem1[0] - elem2[0])
            saida.write(f"{elem1}{elem2} - {dist}\n")
  print("calcDiff terminado!")

def sobrepor(canny: cv.Mat, listas: listsTuple):
  output = gray2bgr(canny)
  for sublista in listas:
    for tupla in sublista:
      output[tupla] = RED
  print("sobrepor terminado!")
  return output

class rThread(Thread):
  def __init__(self, target = None, *args, **kwargs):
    Thread.__init__(self, target = target, *args, **kwargs)
    self._result = None

  def run(self):
    if self._target is None:
      raise RuntimeError("target not specified")
    try: self._result = self._target(*self._args, **self._kwargs)
    except Exception as exc:
      print(f"{type(exc).__name__}: {exc}", file = stderr)

  def join(self, *args, **kwargs):
    Thread.join(self, *args, **kwargs)
    return self._result

if __name__ == "__main__":
  system("cls||clear")
  name, output = openImage(input("Entrie archive: "))
  if not isdir(name): mkdir(name)

  output = cutImage(output)
  cv.imwrite(f"{name}/cutted.png", output)
  output = claheFilter(output)
  cv.imwrite(f"{name}/clahe.png", output)
  canny = cannyFilter(output)
  shape: tuple2int = canny.shape
  cv.imwrite(f"{name}/canny.png", canny)

  deleted, estimat = estimateBack(canny)
  cv.imwrite(f"{name}/estimat.png", estimat)
  cv.imwrite(f"{name}/deleted.png", deleted)

  thread1 = rThread(target = xFilter2, args = [deleted])
  thread2 = rThread(target = xFilter2, args = [estimat])
  thread1.start(); thread2.start()
  deleted, estimat = thread1.join(), thread2.join()
  cv.imwrite(f"{name}/filter1.png", deleted)
  cv.imwrite(f"{name}/filter2.png", estimat)

  thread1 = rThread(target = extract, args = [deleted])
  thread2 = rThread(target = extract, args = [estimat])
  thread1.start(); thread2.start()
  lista1, lista2 = thread1.join(), thread2.join()

  output = juntarImgs(shape, [lista1, lista2])
  cv.imwrite(f"{name}/juntos.png", output)

  thread1 = rThread(target = organize, args = [lista1])
  thread2 = rThread(target = organize, args = [lista2])
  thread1.start(); thread2.start()
  lista1, lista2 = thread1.join(), thread2.join()

  args1 = [lista1, shape, name]
  args2 = [lista2, shape, name]
  thread1 = Thread(target = saveLists, args = args1)
  thread2 = Thread(target = saveLists, args = args2)
  thread1.start(); thread2.start()
  thread1.join(); thread2.join()

  calcDiff(name, lista1, lista2)

  args1 = [output, lista1]
  args2 = [canny, lista1]
  thread1 = rThread(target = sobrepor, args = args1)
  thread2 = rThread(target = sobrepor, args = args2)
  thread1.start(); thread2.start()
  saida1, saida2 = thread1.join(), thread2.join()
  cv.imwrite(f"{name}/sobre1.png", saida1)
  cv.imwrite(f"{name}/sobre2.png", saida2)

  print("Processo Terminado!")