from numpy.typing import NDArray
from numpy import zeros, vstack, errstate, integer, floating
from os.path import isfile, isdir, join
from os import mkdir, scandir
from itertools import pairwise, product
from cv2.typing import MatLike, Size
from cv2 import (imread, imwrite, resize, Canny, cvtColor,
  GaussianBlur, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY,
  adaptiveThreshold, COLOR_BGR2GRAY, COLOR_GRAY2BGR)
from lpmalgos import Ellipsoid, find_clusters
from skeleton import skeletonize
from shutil import rmtree
from typing import Any

NDArray = NDArray[integer[Any] | floating[Any]]
BLACK, WHITE, RED = 0, 255, (0, 0, 255)
NDArrays = list[NDArray]

def bgr2gray(entrie: MatLike):
  return cvtColor(entrie, COLOR_BGR2GRAY)

def gray2bgr(entrie: MatLike):
  return cvtColor(entrie, COLOR_GRAY2BGR)

class imopen:
  __slots__ = ("entrie", "index")

  def __init__(self, entrie: str):
    if not isdir(entrie) and not isfile(entrie):
      raise FileNotFoundError(f"{entrie!r} não existe!")
    self.entrie, self.index = entrie, None

  def __getitem__(self, index: int | slice):
    if isinstance(index, (int, slice)):
      self.index = index
    return self

  def __iter__(self):
    def imopen_core(entrie: str):
      name, extension = entrie.split(".")
      valid = ("bmp", "dib", "jpeg", "jpg", "jpe",
        "jp2", "png", "pnm", "avif", "pbm", "pgm",
        "ppm", "pxm", "webp", "pfm", "sr", "ras",
        "tiff", "tif", "exr", "hdr", "pic")
      if not extension in valid:
        raise TypeError(f"{entrie!r} não é uma imagem!")
      if (image := imread(entrie)) is None:
        raise TypeError(f"{entrie!r} não pôde ser aberto!")
      if isdir(name): rmtree(name)
      return name, bgr2gray(image)

    entrie, index = self.entrie, self.index
    if isfile(entrie):
      yield imopen_core(entrie)
      return
    if isinstance(index, int):
      files = [e for e in scandir(entrie) if e.is_file()]
      yield imopen_core(join(entrie, files[index].name))
      return
    if isinstance(index, slice):
      yield from (imopen_core(join(entrie, e.name)) for e in
        [e for e in scandir(entrie) if e.is_file()][index])
      return
    if index is None:
      yield from (imopen_core(join(entrie, e.name))
        for e in scandir(entrie) if e.is_file())
      return

def cutImage(entrie: MatLike, shape: Size):
  if len(shape) != 2:
    raise TypeError("shape sem tamanho 2!")
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

def dbscanSeparation(entrie: MatLike, quant = 2000):
  def dbscanSeparation_core():
    dim1, dim2 = (entrie == WHITE).nonzero()
    locs = zeros((len(dim1), 3), int)
    locs.T[0], locs.T[1] = dim2, dim1
    ani = Ellipsoid(((.3, 0, 0), (0, 2.6, 0), (0, 0, 0)))
    clusters = find_clusters(locs, ani, 20, 6, 1e-9, 1)
    for cluster in set(clusters):
      dim2, dim1, a = locs[clusters == cluster].T
      if len(dim2) < quant: continue
      yield vstack((dim1, dim2)).T[dim2.argsort()]

  output = list(dbscanSeparation_core())
  print("dbscanSeparation terminado!")
  return output

def curveAdjust(D: NDArray, I: NDArray, n: int):
  D, I = D.astype(float), I.astype(float)
  with errstate(all = "raise"):
    G = D.reshape(-1, 1) ** range(n)
    A, B = (G.T @ G), (G.T @ I)
    L, U = zeros((n, n)), A
    L.flat[::(n + 1)] = 1
    for i, ii in pairwise(range(n)):
      L[ii:, i] = U[ii:, i] / U[i, i]
      U[ii:] -= L[ii:, i, None] * U[i]
    x, y = zeros(n), zeros(n)
    for i in range(n):
      y[i] = B[i] - (L[i] @ y)
    for i in reversed(range(n)):
      temp = y[i] - (U[i] @ x)
      x[i] = temp / U[i, i]
    return (G @ x)

def lineSeparation(entrie: NDArrays):
  MIN, MAX = 550, 6
  curves: NDArrays = []
  basels: NDArrays = []
  for array in entrie:
    (A, B) = array.T
    choice = curves
    line = curveAdjust(B, A, 2)
    res = (abs(line - A) < MAX)
    if (~res).sum() < MIN:
      choice = basels
      A, B = A[res], B[res]
    array = vstack((A, B)).T
    choice.append(array)
  print("lineSeparation terminado!")
  return curves, basels

def saveLines(lines: NDArrays, dname: str, dtype: str, shape: Size):
  if len(shape) != 2: raise TypeError("shape sem tamanho 2!")
  pasta, preta = f"{dname}/lines", zeros(shape, "uint8")
  if not isdir(pasta): mkdir(pasta)
  for i, subarray in enumerate(lines):
    imagem, (dim1, dim2) = preta.copy(), subarray.T
    imagem[dim1, dim2] = WHITE
    imwrite(fr"{pasta}\\{dtype}{i}.png", imagem)
    with open(fr"{pasta}\\{dtype}{i}.txt", "w") as output:
      output.write(f"Tamanho da imagem: {shape}\n")
      output.writelines(f"{elem}\n" for elem in subarray)
  print("saveLines terminado!")

def sobrepor(entrie: MatLike, listas: NDArrays):
  output = gray2bgr(entrie)
  dim1, dim2 = zip(*(e for a in listas for e in a))
  output[dim1, dim2] = RED
  print("sobrepor terminado!")
  return output

def differs(curves: NDArrays, basels: NDArrays, dname: str, const: float):
  if not isdir(pasta := f"{dname}/diffs"): mkdir(pasta)
  ecurves, ebasels = enumerate(curves), enumerate(basels)
  for (c, curve), (b, basel) in product(ecurves, ebasels):
    mean = basel.T[0].mean(None, int)
    values = (mean - curve.T[0]) * const
    with open(fr"{pasta}\\curve{c}base{b}.txt", "w") as output:
      output.writelines(f"({e1}, {mean}), {e2} - {value}\n"
        for (e1, e2), value in zip(curve, values))
  print("differs terminado!")

def components_with_t(base: float, mm_const: float, mm_diff: NDArray,
                      q_comp: float, t_base: float, t_diff: float):
  return (base + (mm_const * mm_diff) - (q_comp * (t_base - t_diff)))

def components_wout_t(base: float, mm_const: float, mm_diff: NDArray):
  return components_with_t(base, mm_const, mm_diff, 0, 0, 0)

d_component = t_component = components_wout_t
h_component = z_component = components_with_t

def differs_new(curves: NDArrays, basels: NDArrays, px_to_mm: float):
  (h, d, z) = curves
  def differs_core():
    for basel in basels:
      meanbase = basel.T[0].mean().round().astype(int)
      diff_h_mm = ((meanbase - h.T[0]) * px_to_mm)
      diff_d_mm = ((meanbase - d.T[0]) * px_to_mm)
      diff_z_mm = ((meanbase - z.T[0]) * px_to_mm)
      yield (diff_h_mm, diff_d_mm, diff_z_mm)
  ret = zip(*differs_core())
  print("differs terminado!")
  return ret

Sequence = tuple[NDArray, ...]
def h_comp_calc(diffs_h: Sequence, h_base: float, h_const: float, hq_comp: float, t_comp: float, dir: str):
  for b, diff_h in enumerate(diffs_h):
    with open(fr"{dir}/diffs/h{b}.txt", "w") as output:
      output.writelines(map(str, h_component(h_base, h_const, diff_h, hq_comp, t_comp)))

def d_comp_calc(diffs_d: Sequence, d_base: float, d_const: float, dir: str):
  for b, diff_d in enumerate(diffs_d):
    with open(fr"{dir}/diffs/d{b}.txt", "w") as output:
      output.writelines(map(str, d_component(d_base, d_const, diff_d)))

def z_comp_calc(diffs_z: Sequence, z_base: float, z_const: float, zq_comp: float, t_comp: float, dir: str):
  for b, diff_z in enumerate(diffs_z):
    with open(fr"{dir}/diffs/z{b}.txt", "w") as output:
      output.writelines(map(str, z_component(z_base, z_const, diff_z, zq_comp, t_comp)))

def main():
  shape, const = (1800, 4590), (200 / 4590)
  for name, opened in imopen("Imagens"):
    print(f"Imagem atual: {name}")
    if not isdir(name): mkdir(name)

    cutted = cutImage(opened, shape)
    imwrite(f"{name}/cutted.png", cutted)
    gauss = gaussProcess(cutted)
    imwrite(f"{name}/gauss.png", gauss)
    canny = cannyFilter(gauss)
    imwrite(f"{name}/canny.png", canny)

    skeleton = skeletonize(canny, 15)
    imwrite(f"{name}/skeleton.png", skeleton)

    separed = dbscanSeparation(skeleton)
    curves, basels = lineSeparation(separed)

    saveLines(curves, name, "curve", shape)
    saveLines(basels, name, "basel", shape)
    differs(curves, basels, name, const)

    dbscan1 = sobrepor(skeleton, curves)
    dbscan2 = sobrepor(canny, curves)
    imwrite(f"{name}/dbscan1.png", dbscan1)
    imwrite(f"{name}/dbscan2.png", dbscan2)
    print("\n----------------------\n")

  print("Processo Terminado!")

if __name__ == "__main__": main()