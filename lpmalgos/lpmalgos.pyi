from numpy import floating, integer
from numpy.typing import NDArray
from typing import overload, Any

def angular_distance(
  A: NDArray[floating[Any]],
  B: NDArray[floating[Any]],
  C: NDArray[floating[Any]]
) -> float:
  ...

def find_clusters(
  locs: NDArray[floating[Any]],
  anisotropy: Ellipsoid,
  r_tol: float,
  angular_tol: float,
  support_theshold: float,
  min_support_size: int
) -> NDArray[integer[Any]]:
  ...

class EllipsoidInfo:
  def r1() -> float: ...
  def r2() -> float: ...
  def r3() -> float: ...
  def azimuth() -> float: ...
  def dip() -> float: ...
  def rake() -> float: ...

class Ellipsoid:
  @overload
  def __init__() -> Ellipsoid: ...

  @overload
  def __init__(
    r1: float,
    r2: float,
    r3: float,
    azimuth: float,
    dip: float,
    rake: float
  ) -> Ellipsoid:
    ...

  @overload
  def __init__(
    matrix: NDArray[floating[Any]]
  ) -> Ellipsoid:
    ...

  @overload
  def __init__(
    ellipsoid_info: EllipsoidInfo
  ) -> Ellipsoid:
    ...

  @overload
  def forward(): ...

  @overload
  def forward(): ...

  @overload
  def backward(): ...

  @overload
  def backward(): ...