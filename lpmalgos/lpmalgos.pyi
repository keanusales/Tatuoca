from typing import Sequence, overload, Any
from numpy import floating, integer
from numpy.typing import NDArray

ArrayLike = Sequence[Sequence[float]] | NDArray[floating[Any]]

def angular_distance(
  A: ArrayLike,
  B: ArrayLike,
  C: ArrayLike
) -> float: ...

def find_clusters(
  locs: NDArray[floating[Any]],
  anisotropy: Ellipsoid,
  r_tol: float,
  angular_tol: float,
  support_theshold: float,
  min_support_size: int
) -> NDArray[integer[Any]]: ...

class EllipsoidInfo:
  def r1(self) -> float: ...
  def r2(self) -> float: ...
  def r3(self) -> float: ...
  def azimuth(self) -> float: ...
  def dip(self) -> float: ...
  def rake(self) -> float: ...

class Ellipsoid:
  @overload
  def __init__(self) -> None: ...

  @overload
  def __init__(self,
    r1: float,
    r2: float,
    r3: float,
    azimuth: float,
    dip: float,
    rake: float
  ) -> None: ...

  @overload
  def __init__(self,
    matrix: ArrayLike
  ) -> None: ...

  @overload
  def __init__(self,
    ellipsoid_info: EllipsoidInfo
  ) -> None: ...

  @overload
  def forward(self,
    loc: ArrayLike
  ) -> NDArray[floating[Any]]: ...

  @overload
  def forward(self,
    locs: NDArray[floating[Any]]
  ) -> NDArray[floating[Any]]: ...

  @overload
  def backward(self,
    loc: ArrayLike
  ) -> NDArray[floating[Any]]: ...

  @overload
  def backward(self,
    locs: NDArray[floating[Any]]
  ) -> NDArray[floating[Any]]: ...

  def matrix(self) -> NDArray[floating[Any]]: ...
  def inv_matrix(self) -> NDArray[floating[Any]]: ...

  def major_axis(self) -> NDArray[floating[Any]]: ...
  def mid_axis(self) -> NDArray[floating[Any]]: ...
  def minor_axis(self) -> NDArray[floating[Any]]: ...

  def info(self) -> EllipsoidInfo: ...
  def __str__(self) -> str: ...

def extract_ellipsoid_info(
  T: ArrayLike
) -> EllipsoidInfo: ...

def sort_matrix3d(
  T: ArrayLike,
  orthogonalize: bool = True
) -> NDArray[floating[Any]]: ...

def orthogonolize_axes(
  T: ArrayLike,
  sort: bool = True
) -> NDArray[floating[Any]]: ...

class Neighborhood:
  @overload
  def __init__(self,
    locs: NDArray[floating[Any]],
    ellipsoid: Ellipsoid
  ) -> None: ...

  @overload
  def __init__(self,
    locs: NDArray[floating[Any]]
  ) -> None: ...

  @overload
  def find_neighbors(self,
    loc: ArrayLike,
    max_size: int
  ) -> NDArray[integer[Any]]: ...

  @overload
  def find_neighbors(self,
    loc: ArrayLike,
    max_radius: float
  ) -> NDArray[integer[Any]]: ...

  def nearest_neighbor(
    loc: ArrayLike
  ) -> int: ...