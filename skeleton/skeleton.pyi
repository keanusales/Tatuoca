from numpy.typing import NDArray
from numpy import integer
from typing import Any

def skeletonize(
  entrie: NDArray[integer[Any]],
  distance: int
) -> NDArray[integer[Any]]: ...