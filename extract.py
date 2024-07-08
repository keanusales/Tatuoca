from numpy.typing import NDArray
from numpy import integer, floating
from numpy import zeros, vstack
from os.path import isfile, isdir, join
from os import mkdir, scandir
from itertools import product
from cv2.typing import MatLike, Size
from cv2 import (cvtColor, imread, imwrite, resize, Canny,
  GaussianBlur, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY,
  adaptiveThreshold, COLOR_BGR2GRAY, COLOR_GRAY2BGR)
from lpmalgos import Ellipsoid, find_clusters
from skeleton import skeletonize
from shutil import rmtree
from typing import Any

NDArray = NDArray[integer[Any] | floating[Any]]
BLACK, WHITE, RED = 0, 255, (0, 0, 255)
larrs = list[NDArray]

def checkValidImageFormat(extension: str):
  valid = ("bmp", "dib", "jpeg", "jpg", "jpe",
    "jp2", "png", "pnm", "avif", "pbm", "pgm",
    "ppm", "pxm", "webp", "pfm", "sr", "ras",
    "tiff", "tif", "exr", "hdr", "pic")
  if not extension in valid:
    raise TypeError("Não é uma imagem!")

def bgr2gray(entrie: MatLike):
  return cvtColor(entrie, COLOR_BGR2GRAY)

def gray2bgr(entrie: MatLike):
  return cvtColor(entrie, COLOR_GRAY2BGR)

def imopen(entrie: str):
  def imopen_core(entrie: str):
    name, ext = entrie.split(".")
    checkValidImageFormat(ext)
    if isdir(name): rmtree(name)
    return name, bgr2gray(imread(entrie))

  if isfile(entrie):
    yield imopen_core(entrie)
    return
  if isdir(entrie):
    yield from (imopen_core(join(entrie, e.name))
      for e in scandir(entrie) if e.is_file())
    return

  raise FileNotFoundError(f"{entrie!r} ñ existe!")

def cutImage(entrie: MatLike, shape: Size):
  if len(shape) != 2: raise TypeError(
    "\"shape\" não tem tamanho 2!")
  x1, x2, y1, y2 = 180, 2445, 305, 6095
  cutted = entrie[x1:x2, y1:y2]
  cutted = resize(cutted, shape[::-1])
  print("cutImage terminado!")
  return cutted

def gaussProcess(entrie: MatLike, size = 19, C = 10):
  output = adaptiveThreshold(entrie, 255,
    ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, size, C)
  output = GaussianBlur(output, (11, 11), 0)
  print("gaussProcess terminado!")
  return output

def cannyFilter(entrie: MatLike):
  output = Canny(entrie, 200, 255, L2gradient = True)
  print("cannyFilter terminado!")
  return output

def separeLines(entrie: MatLike, quant = 2000):
  def separeLines_core():
    dim1, dim2 = (entrie == WHITE).nonzero()
    locs = zeros((len(dim1), 3), int)
    locs[:, 0], locs[:, 1] = dim2, dim1
    ani = Ellipsoid(((.3, 0, 0), (0, 2.6, 0), (0, 0, 0)))
    clusters = find_clusters(locs, ani, 20, 6, 1e-9, 1)
    for cluster in set(clusters):
      dim2, dim1, a = locs[clusters == cluster].T
      if len(dim2) < quant: continue
      yield vstack((dim1, dim2)).T[dim2.argsort()]

  output = [*separeLines_core()]
  print("separeLines terminado!")
  return output

def meanRemove(entrie: larrs):
  MIN, MAX = 550, 5
  curves: larrs = []
  basels: larrs = []
  for array in entrie:
    (A, B) = array.T
    choice = curves
    mean = A.mean(dtype = int)
    res = (abs(A - mean) > MAX)
    if res.sum() < MIN:
      choice, res = basels, ~res
      A, B = A[res], B[res]
    array = vstack((A, B)).T
    choice.append(array)
  print("meanRemove terminado!")
  return curves, basels

def saveLines(lines: larrs, dname: str, dtype: str, shape: Size):
  if len(shape) != 2: raise TypeError("shape sem tam. 2!")
  pasta, preta = f"{dname}/lines", zeros(shape, "u1")
  if not isdir(pasta): mkdir(pasta)
  for i, subarray in enumerate(lines):
    imagem, (dim1, dim2) = preta.copy(), subarray.T
    imagem[dim1, dim2] = WHITE
    imwrite(fr"{pasta}\\{dtype}{i}.png", imagem)
    with open(fr"{pasta}\\{dtype}{i}.txt", "w") as output:
      output.write(f"Tam.: {shape}\n")
      output.writelines(map(str, subarray))
  print("saveLines terminado!")

def sobrepor(entrie: MatLike, listas: larrs):
  output = gray2bgr(entrie)
  dim1, dim2 = zip(*(e for a in listas for e in a))
  output[dim1, dim2] = RED
  print("sobrepor terminado!")
  return output

def differs(curves: larrs, basels: larrs, dname: str, alt: int):
  pasta, const = f"{dname}/diffs", (200 / alt)
  if not isdir(pasta): mkdir(pasta)
  ecurves, ebasels = enumerate(curves), enumerate(basels)
  for (c, curve), (b, basel) in product(ecurves, ebasels):
    mean = basel.T[0].mean(dtype = int)
    with open(fr"{pasta}\\curve{c}base{b}.txt", "w") as saida:
      for (e1, e2) in curve:
        value = (mean - e1) * const
        el1, el2 = (e1, e2), (mean, e2)
        saida.write(f"{el1}{el2} - {value}\n")
  print("differs terminado!")

shape, alt = (1800, 4590), 4590
images = enumerate(imopen(r"Imagens"))
for i, (name, opened) in images:
  print(f"{i + 1} - Imagem {name}")
  if not isdir(name): mkdir(name)

  cutted = cutImage(opened, shape)
  imwrite(f"{name}/cutted.png", cutted)
  gauss = gaussProcess(cutted)
  imwrite(f"{name}/gauss.png", gauss)
  canny = cannyFilter(gauss)
  imwrite(f"{name}/canny.png", canny)

  skeleton = skeletonize(canny, 12)
  imwrite(f"{name}/skeleton.png", skeleton)

  separed = separeLines(skeleton)
  curves, basels = meanRemove(separed)

  saveLines(curves, name, "curve", shape)
  saveLines(basels, name, "basel", shape)
  differs(curves, basels, name, alt)

  sobre1 = sobrepor(skeleton, curves)
  sobre2 = sobrepor(canny, curves)
  imwrite(f"{name}/sobre1.png", sobre1)
  imwrite(f"{name}/sobre2.png", sobre2)
  print("\n----------------------\n")

print("Processo Terminado!")