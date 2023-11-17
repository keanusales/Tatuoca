from extract import listsTuple, shape
from itertools import product
from os.path import isdir
from os import mkdir

alt = shape[0]
h_pixel, d_pixel, z_pixel = (200/alt), (200/alt), (200/alt)
variations = (h_pixel, d_pixel, z_pixel)

def calcDiff(dname: str, curves: listsTuple, basels: listsTuple):
  pasta = f"{dname}/calculoDiff"
  if not isdir(pasta): mkdir(pasta)
  ncurves = enumerate(zip(curves, variations))
  nbasels = enumerate(basels)
  for (a, (sub1, var)), (b, sub2) in product(ncurves, nbasels):
    with open(f"{pasta}/curve{a}base{b}.txt", "w") as saida:
      pos2, len2 = 0, len(sub2)
      for el1 in sub1:
        e1, e2 = el1
        for i in range(pos2, len2):
          e3, e4 = el2 = sub2[i]
          if e2 == e4:
            pos2, value = (i + 1), var*(e3 - e1)
            saida.write(f"{el1}{el2} - {value}\n")
            break
  print("calcDiff terminado!")