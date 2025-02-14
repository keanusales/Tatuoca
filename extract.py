from numpy.typing import NDArray
from numpy import zeros, vstack, errstate, integer, floating
from os.path import isfile, isdir, join, splitext
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

def bgr2gray(image: MatLike) -> MatLike:
  """
  Converte uma imagem de BGR para escala de cinza.
  
  Args:
    image (MatLike): Imagem em formato BGR.
  
  Returns:
    MatLike: Imagem em escala de cinza.
  """
  return cvtColor(image, COLOR_BGR2GRAY)

def gray2bgr(image: MatLike) -> MatLike:
  """
  Converte uma imagem de escala de cinza para BGR.
  
  Args:
    image (MatLike): Imagem em escala de cinza.
  
  Returns:
    MatLike: Imagem em formato BGR.
  """
  return cvtColor(image, COLOR_GRAY2BGR)

class ImageOpener:
  """
  Classe para abrir imagens de um diretório ou arquivo.
  """
  __slots__ = ("path", "index")

  def __init__(self, path: str):
    """
    Inicializa a classe com o caminho do arquivo ou diretório.
    
    Args:
      path (str): Caminho do arquivo ou diretório.
    
    Raises:
      FileNotFoundError: Se o caminho não existir.
    """
    if not isdir(path) and not isfile(path):
      raise FileNotFoundError(f"{path!r} não existe!")
    self.path, self.index = path, None

  def __getitem__(self, index: int | slice):
    """
    Define o índice ou fatia para iteração.
    
    Args:
      index (int | slice): Índice ou fatia.
    
    Returns:
      self: Instância da classe.
    """
    if isinstance(index, (int, slice)):
      self.index = index
    return self

  def __iter__(self):
    """
    Itera sobre os arquivos de imagem no diretório ou arquivo.
    
    Yields:
      tuple: Nome do arquivo e imagem em escala de cinza.
    """
    def open_image_core(path: str):
      name, extension = splitext(path)
      valid_extensions = (".bmp", ".dib", ".jpeg", ".jpg",
        ".jpe", ".jp2", ".png", ".pnm", ".avif", ".pbm",
        ".pgm", ".ppm", ".pxm", ".webp", ".pfm", ".sr",
        ".ras", ".tiff", ".tif", ".exr", ".hdr", ".pic")
      if extension not in valid_extensions:
        raise TypeError(f"{path!r} não é uma imagem!")
      if (image := imread(path)) is None:
        raise TypeError(f"{path!r} não pôde ser aberto!")
      if isdir(name): rmtree(name)
      return name, bgr2gray(image)

    path, index = self.path, self.index
    if isfile(path):
      yield open_image_core(path)
      return
    if isinstance(index, int):
      files = [e for e in scandir(path) if e.is_file()]
      yield open_image_core(join(path, files[index].name))
      return
    if isinstance(index, slice):
      iter(open_image_core(join(path, e.name)) for e in
        [e for e in scandir(path) if e.is_file()][index])
      return
    if index is None:
      iter(open_image_core(join(path, e.name))
        for e in scandir(path) if e.is_file())
      return

def cut_image(image: MatLike, shape: Size) -> MatLike:
  """
  Corta a imagem em uma região específica e redimensiona.

  Args:
    image (MatLike): Imagem de entrada.
    shape (Size): Tamanho desejado da imagem.

  Raises:
    TypeError: Se o shape não tiver tamanho 2.

  Returns:
    MatLike: Imagem cortada e redimensionada.
  """
  if len(shape) != 2:
    raise TypeError("shape sem tamanho 2!")
  x1, x2, y1, y2 = 180, 2445, 305, 6095
  cropped = image[x1:x2, y1:y2]
  resized = resize(cropped, shape[::-1])
  print("cut_image terminado!")
  return resized

def gauss_process(image: MatLike, size: int = 19, C: int = 10) -> MatLike:
  """
  Aplica processamento Gaussiano na imagem.

  Args:
    image (MatLike): Imagem de entrada.
    size (int, optional): Tamanho do bloco. Padrão é 19.
    C (int, optional): Constante subtraída da média. Padrão é 10.

  Returns:
    MatLike: Imagem processada.
  """
  output = adaptiveThreshold(image, 255,
    ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, size, C)
  output = GaussianBlur(output, (11, 11), 0)
  print("gauss_process terminado!")
  return output

def canny_filter(image: MatLike) -> MatLike:
  """
  Aplica filtro Canny na imagem.

  Args:
    image (MatLike): Imagem de entrada.

  Returns:
    MatLike: Imagem filtrada.
  """
  output = Canny(image, 200, 255, L2gradient=True)
  print("canny_filter terminado!")
  return output

def dbscan_separation(image: MatLike, min_points: int = 2000) -> NDArrays:
  """
  Separa clusters usando DBSCAN.

  Args:
    image (MatLike): Imagem de entrada.
    min_points (int, optional): Número mínimo de pontos em um cluster. Padrão é 2000.

  Returns:
    NDArrays: Lista de clusters separados.
  """
  def dbscan_separation_core():
    dim1, dim2 = (image == WHITE).nonzero()
    locs = zeros((len(dim1), 3), int)
    locs.T[0], locs.T[1] = dim2, dim1
    ani = Ellipsoid(((.3, 0, 0), (0, 2.6, 0), (0, 0, 0)))
    clusters = find_clusters(locs, ani, 20, 6, 1e-9, 1)
    for cluster in set(clusters):
      dim2, dim1, _ = locs[clusters == cluster].T
      if len(dim2) < min_points: continue
      yield vstack((dim1, dim2)).T[dim2.argsort()]

  output = list(dbscan_separation_core())
  print("dbscan_separation terminado!")
  return output

def curve_adjust(D: NDArray, I: NDArray, degree: int) -> NDArray:
  """
  Ajusta curvas usando um polinômio de grau n.

  Args:
    D (NDArray): Dados de entrada.
    I (NDArray): Valores de saída.
    degree (int): Grau do polinômio.

  Returns:
    NDArray: Curva ajustada.
  """
  D, I = D.astype(float), I.astype(float)
  with errstate(all="raise"):
    G = D.reshape(-1, 1) ** range(degree)
    A, B = (G.T @ G), (G.T @ I)
    L, U = zeros((degree, degree)), A
    L.flat[::(degree + 1)] = 1
    for i, ii in pairwise(range(degree)):
      L[ii:, i] = U[ii:, i] / U[i, i]
      U[ii:] -= L[ii:, i, None] * U[i]
    x, y = zeros(degree), zeros(degree)
    for i in range(degree):
      y[i] = B[i] - (L[i] @ y)
    for i in reversed(range(degree)):
      temp = y[i] - (U[i] @ x)
      x[i] = temp / U[i, i]
    return (G @ x)

def line_separation(clusters: NDArrays) -> tuple[NDArrays, NDArrays]:
  """
  Separa linhas em curvas e bases.

  Args:
    clusters (NDArrays): Lista de clusters.

  Returns:
    tuple[NDArrays, NDArrays]: Curvas e bases separadas.
  """
  MIN_POINTS, MAX_DIFF = 550, 6
  curves: NDArrays = []
  baselines: NDArrays = []
  for cluster in clusters:
    (A, B) = cluster.T
    choice = curves
    line = curve_adjust(B, A, 2)
    res = (abs(line - A) < MAX_DIFF)
    if (~res).sum() < MIN_POINTS:
      choice = baselines
      A, B = A[res], B[res]
    cluster = vstack((A, B)).T
    choice.append(cluster)
  print("line_separation terminado!")
  return curves, baselines

def save_lines(lines: NDArrays, directory: str, dtype: str, shape: Size):
  """
  Salva linhas em arquivos de imagem e texto.

  Args:
    lines (NDArrays): Lista de linhas.
    directory (str): Diretório para salvar os arquivos.
    dtype (str): Tipo de linha (curva ou base).
    shape (Size): Tamanho da imagem.

  Raises:
    TypeError: Se o shape não tiver tamanho 2.
  """
  if len(shape) != 2:
    raise TypeError("shape sem tamanho 2!")
  lines_dir = f"{directory}/lines"
  black_image = zeros(shape, "uint8")
  if not isdir(lines_dir): mkdir(lines_dir)
  for i, subarray in enumerate(lines):
    image, (dim1, dim2) = black_image.copy(), subarray.T
    image[dim1, dim2] = WHITE
    imwrite(fr"{lines_dir}\\{dtype}{i}.png", image)
    with open(fr"{lines_dir}\\{dtype}{i}.txt", "w") as output:
      output.write(f"Tamanho da imagem: {shape}\n")
      output.writelines(f"{elem}\n" for elem in subarray)
  print("save_lines terminado!")

def overlay_lines(image: MatLike, lines: NDArrays) -> MatLike:
  """
  Sobrepõe linhas em uma imagem.

  Args:
    image (MatLike): Imagem de entrada.
    lines (NDArrays): Lista de linhas.

  Returns:
    MatLike: Imagem com linhas sobrepostas.
  """
  output = gray2bgr(image)
  dim1, dim2 = zip(*(e for line in lines for e in line))
  output[dim1, dim2] = RED
  print("overlay_lines terminado!")
  return output

def calculate_differences(curves: NDArrays, baselines: NDArrays, directory: str, const: float):
  """
  Calcula diferenças entre curvas e bases.

  Args:
    curves (NDArrays): Lista de curvas.
    baselines (NDArrays): Lista de bases.
    directory (str): Diretório para salvar os arquivos.
    const (float): Constante de conversão.
  """
  differences_dir = f"{directory}/diffs"
  if not isdir(differences_dir): mkdir(differences_dir)
  curves_and_baselines = product(enumerate(curves), enumerate(baselines))
  for (curve_index, curve), (baseline_index, baseline) in curves_and_baselines:
    mean = baseline.T[0].mean(None, int)
    values = (mean - curve.T[0]) * const
    with open(fr"{differences_dir}\\curve{curve_index}base{baseline_index}.txt", "w") as output:
      output.writelines(f"({e1}, {mean}), {e2} - {value}\n" for (e1, e2), value in zip(curve, values))
  print("calculate_differences terminado!")

def components_with_t(base: float, mm_const: float, mm_diff: NDArray,
                      q_comp: float, t_base: float, t_diff: float) -> NDArray:
  """
  Calcula componentes com t.

  Args:
    base (float): Valor base.
    mm_const (float): Constante de conversão.
    mm_diff (NDArray): Diferença em milímetros.
    q_comp (float): Componente q.
    t_base (float): Valor base de t.
    t_diff (float): Diferença de t.

  Returns:
    NDArray: Componentes calculados.
  """
  return (base + (mm_const * mm_diff) - (q_comp * (t_base - t_diff)))

def components_without_t(base: float, mm_const: float, mm_diff: NDArray) -> NDArray:
  """
  Calcula componentes sem t.

  Args:
    base (float): Valor base.
    mm_const (float): Constante de conversão.
    mm_diff (NDArray): Diferença em milímetros.

  Returns:
    NDArray: Componentes calculados.
  """
  return components_with_t(base, mm_const, mm_diff, 0, 0, 0)

d_component = t_component = components_without_t
h_component = z_component = components_with_t

def calculate_new_differences(curves: NDArrays, baselines: NDArrays,
    px_to_mm: float) -> tuple[NDArray, NDArray, NDArray]:
  """
  Calcula novas diferenças entre curvas e bases.

  Args:
    curves (NDArrays): Lista de curvas.
    baselines (NDArrays): Lista de bases.
    px_to_mm (float): Conversão de pixels para milímetros.

  Returns:
    tuple[NDArray, NDArray, NDArray]: Diferenças calculadas.
  """
  h_curve, d_curve, z_curve = curves
  def calculate_core():
    for baseline in baselines:
      mean_base = baseline.T[0].mean().round().astype(int)
      diff_h_mm = ((mean_base - h_curve.T[0]) * px_to_mm)
      diff_d_mm = ((mean_base - d_curve.T[0]) * px_to_mm)
      diff_z_mm = ((mean_base - z_curve.T[0]) * px_to_mm)
      yield (diff_h_mm, diff_d_mm, diff_z_mm)
  result = zip(*calculate_core())
  print("calculate_new_differences terminado!")
  return result

Sequence = tuple[NDArray, ...]

def calculate_h_components(diffs_h: Sequence, h_base: float, h_const: float,
    hq_comp: float, t_comp: float, directory: str):
  """
  Calcula componentes h.

  Args:
    diffs_h (Sequence): Diferenças h.
    h_base (float): Valor base de h.
    h_const (float): Constante de h.
    hq_comp (float): Componente q de h.
    t_comp (float): Componente t.
    directory (str): Diretório para salvar os arquivos.
  """
  for index, diff_h in enumerate(diffs_h):
    with open(fr"{directory}/diffs/h{index}.txt", "w") as output:
      output.writelines(map(str, h_component(h_base, h_const, diff_h, hq_comp, t_comp)))

def calculate_d_components(diffs_d: Sequence, d_base: float, d_const: float, directory: str):
    """
    Calcula componentes d.

    Args:
      diffs_d (Sequence): Diferenças d.
      d_base (float): Valor base de d.
      d_const (float): Constante de d.
      directory (str): Diretório para salvar os arquivos.
    """
    for index, diff_d in enumerate(diffs_d):
      with open(fr"{directory}/diffs/d{index}.txt", "w") as output:
        output.writelines(map(str, d_component(d_base, d_const, diff_d)))

def calculate_z_components(diffs_z: Sequence, z_base: float, z_const: float,
      zq_comp: float, t_comp: float, directory: str):
  """
  Calcula componentes z.

  Args:
    diffs_z (Sequence): Diferenças z.
    z_base (float): Valor base de z.
    z_const (float): Constante de z.
    zq_comp (float): Componente q de z.
    t_comp (float): Componente t.
    directory (str): Diretório para salvar os arquivos.
  """
  for index, diff_z in enumerate(diffs_z):
    with open(fr"{directory}/diffs/z{index}.txt", "w") as output:
      output.writelines(map(str, z_component(z_base, z_const, diff_z, zq_comp, t_comp)))

def main():
  """
  Função principal para processar as imagens.
  """
  shape, const = (1800, 4590), (200 / 4590)
  for name, opened in ImageOpener("Imagens"):
    print(f"Imagem atual: {name}")
    if not isdir(name): mkdir(name)

    cropped_image = cut_image(opened, shape)
    imwrite(f"{name}/cutted.png", cropped_image)
    gauss_image = gauss_process(cropped_image)
    imwrite(f"{name}/gauss.png", gauss_image)
    canny_image = canny_filter(gauss_image)
    imwrite(f"{name}/canny.png", canny_image)

    skeleton_image = skeletonize(canny_image, 15)
    imwrite(f"{name}/skeleton.png", skeleton_image)

    separated_clusters = dbscan_separation(skeleton_image)
    curves, baselines = line_separation(separated_clusters)

    save_lines(curves, name, "curve", shape)
    save_lines(baselines, name, "basel", shape)
    calculate_differences(curves, baselines, name, const)

    dbscan1 = overlay_lines(skeleton_image, curves)
    dbscan2 = overlay_lines(canny_image, curves)
    imwrite(f"{name}/dbscan1.png", dbscan1)
    imwrite(f"{name}/dbscan2.png", dbscan2)
    print("\n----------------------\n")

  print("Processo Terminado!")

if __name__ == "__main__": main()