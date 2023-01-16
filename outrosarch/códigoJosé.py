import cv2
import numpy as np
import outrosarch.utils as utils
from pathlib import Path
import os
########################################################################

########################################################################

# variáveis
count = 0
loop = True
outcount = 0

# GUI
layout = [[sg.Combo(sorted(sg.user_settings_get_entry('-filenames-', [])),
          default_value = sg.user_settings_get_entry('-last filename-', ''),
          size = (50, 1), key = '-FILENAME-'), sg.FolderBrowse(),
          sg.B('Clear History')], [sg.Button('Iniciar'), sg.Button('Sair')]]

window = sg.Window('Digitalizador de documentos 0.3b', layout)

# Funcoes
def tratamento_potrace():
  THISDIR = str(Path(__file__).resolve().parent)
  with open(f"{THISDIR}/logo.svg", "w") as bw:
    bw.write(trace(f"{THISDIR}/myImage0.png", True))

def svg_para_pdf():
  drawing = svg2rlg("logo.svg")
  renderPDF.drawToFile(drawing, "final2.pdf")

# Corpo do programa
while True:
  event, values = window.read()

  if event in (sg.WIN_CLOSED, 'Sair'): break

  if event == 'Iniciar':
    # If OK, then need to add the filename to the list of files and also set as the last used filename
    sg.user_settings_set_entry('-filenames-',
      [set(sg.user_settings_get_entry('-filenames-', []) + [values['-FILENAME-'], ])])
    sg.user_settings_set_entry('-last filename-', values['-FILENAME-'])
    pathfiles = str(values.get('-FILENAME-'))
    for imagefiles in os.listdir(pathfiles):
      outcount += 1
      imagepath = os.path.join(pathfiles, imagefiles)
      img = cv2.imread(imagepath)

      # TRATAMENTO PARA DETECTAR CONTORNOS
      heightImg = img.shape[0]
      widthImg = img.shape[1]
      imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERTE ESCALA DE CINZA
      imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)  # ADICIONA GAUSS
      kernel = np.ones((5, 5))
      imgPrep1 = cv2.erode(imgBlur, kernel)  # ADICIONA EROSÃO
      imgPrep2 = cv2.morphologyEx(imgPrep1, cv2.MORPH_OPEN, kernel)
      imgPrep3 = cv2.morphologyEx(imgPrep2, cv2.MORPH_CLOSE, kernel)
      imgContours = img.copy()  # COPIA PARA DEBUG
      imgBigContour = img.copy()  # COPIA PARA DEBUG
      imgPrep4 = cv2.Canny(imgPrep3, 20, 240)  # ADICIONA Canny
      imgPrepFinal = cv2.dilate(imgPrep4, kernel)  # ADICIONA DILATACAO
      cv2.imwrite(f'{pathfiles}/{imagefiles}_{outcount}_erode.jpg', imgPrepFinal)
      contours, hierarchy = cv2.findContours(imgPrepFinal, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # ACHA TODOS
      cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DESENHA CONTORNOS
      cv2.imwrite(f'{pathfiles}/{imagefiles}_{outcount}_contour.jpg', imgContours)

      biggest, maxArea = utils.biggestContour(contours)  # FIND THE BIGGEST CONTOUR

      if biggest.size != 0:
        biggest = utils.reorder(biggest)
        cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
        imgBigContour = utils.drawRectangle(imgBigContour, biggest, 2)
        cv2.imwrite(f"./MyImageBiggestContour{count}.png", imgBigContour)
        pts1 = np.float32(biggest)  # PREPARAR PONTOS PARA MUDANÇA PERSPECTIVA
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])  # PREPARA OS SEGUNDOS PONTOS PARA MUDANÇA
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        print(biggest)
        print('----------------------------------------')
        print(pts1)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        #  REMOVER 20 PIXELS DOS LADOS
        imgWarpColored = imgWarpColored[20:imgWarpColored.shape[0] - 20, 20:imgWarpColored.shape[1] - 20]
        imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))
      else: imgWarpColored = imgContours
      cv2.imwrite(f'{pathfiles}/{imagefiles}_{outcount}.jpg', imgWarpColored)

  elif event == 'Clear History':
      sg.user_settings_set_entry('-filenames-', [])
      sg.user_settings_set_entry('-last filename-', '')
      window['-FILENAME-'].update(values=[], value='')

window.close()