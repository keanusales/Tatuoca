from cv2 import Mat
import cython as cy

BLACK: cy.int = 0
WHITE: cy.int = 255

def xFilter(entrie: Mat, length: cy.int = 5) -> Mat:
  output = entrie.copy()
  @cy.cfunc
  def funcao1(pair1: cy.int, pair2: cy.int):
    @cy.cfunc
    def funcao2(cord1: cy.int, cord2: cy.int) -> cy.bint:
      pixel1 = output[cord1, pair2]
      pixel2 = output[cord2, pair2]
      if pixel1 == pixel2 == WHITE:
        for x in range(cord1, cord2 + 1):
          output[x, pair2] = BLACK
        output[pair1, pair2] = WHITE
        return True
      return False
    cord1: cy.int = pair1 - length
    cord2: cy.int = pair1 + length
    while cord1 != cord2:
      if funcao2(cord1, cord2): break
      cord1 += 1
      if funcao2(cord1, cord2): break
      cord1 -= 1; cord2 -= 1
      if funcao2(cord1, cord2): break
      cord1 += 1
  altura: cy.int = output.shape[0]
  largura: cy.int = output.shape[1]
  atr1, atr2 = length + 1, altura - length
  for x in range(atr1, atr2):
    for y in range(largura):
      funcao1(x, y)
  print("xFilter terminado!")
  return output