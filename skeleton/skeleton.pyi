from numpy import ndarray, dtype, integer

def skeletonize(
  entrie: ndarray[tuple[int, int], dtype[integer]],
  distance: int
) -> ndarray[tuple[int, int], dtype[integer]]: ...