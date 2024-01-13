from extract import (
  imopen, isdir, mkdir,
  imwrite, cutImage,
  gaussThresh, gaussBlur,
  cannyFilter, separeLines,
  skeletonize, extractWhites,
  juntarImgs, organize,
  saveLists, sobrepor
)
from convert import calcDiff
from os import system

system("cls||clear")
name, output = imopen(input("Entrie archive: "))
if not isdir(name): mkdir(name)

output = cutImage(output)
imwrite(f"{name}/cutted.png", output)
output = gaussThresh(output)
output = gaussBlur(output)
imwrite(f"{name}/gauss.png", output)
canny = cannyFilter(output)
imwrite(f"{name}/canny.png", canny)

deleted, estimat = separeLines(canny)
imwrite(f"{name}/estimat.png", estimat)
imwrite(f"{name}/deleted.png", deleted)

deleted, estimat = skeletonize(deleted), skeletonize(estimat)
imwrite(f"{name}/filter1.png", deleted)
imwrite(f"{name}/filter2.png", estimat)

lista1, lista2 = extractWhites(deleted), extractWhites(estimat)
output = juntarImgs([lista1, lista2])
imwrite(f"{name}/juntos.png", output)

lista1, lista2 = organize(lista1), organize(lista2)
saveLists(lista1, "curve", name)
saveLists(lista2, "base", name)
calcDiff(name, lista1, lista2)

saida1 = sobrepor(output, lista1)
saida2 = sobrepor(canny, lista1)
imwrite(f"{name}/sobre1.png", saida1)
imwrite(f"{name}/sobre2.png", saida2)

print("Processo Terminado!")