# distutils: define_macros = NPY_NO_DEPRECATED_API
# cython: binding = False, initializedcheck = False
# cython: boundscheck = False, wraparound = False
# cython: language_level = 3, cdivision = True
# distutils: extra_compile_args = /openmp
# distutils: language = c++

from numpy cimport PyArray_Copy as copy
from numpy cimport ndarray, uint8_t
from cython.parallel import prange
from numpy cimport import_array

import_array()

cdef extern from "<thread>" namespace "std::thread" nogil:
  unsigned hardware_concurrency() noexcept

cdef unsigned check_threads() nogil:
  cdef unsigned threads = hardware_concurrency()
  if not threads: return 1
  return threads

cdef uint8_t BLACK = 0, WHITE = 255

cdef ndarray __skeletonize__(
      ndarray[uint8_t, ndim = 2] entrie,
      int distance):
  cdef ndarray entriecopy = copy(entrie)
  cdef uint8_t[:, :] entrieview = entriecopy
  cdef int rows = <int> entrieview.shape[0]
  cdef int cols = <int> entrieview.shape[1]
  cdef int maxd = rows - distance
  cdef int lin1, lin2, col, pos1, pos2, pos
  cdef bint white_detect

  cdef unsigned threads = check_threads()
  for col in prange(cols, nogil = True,
      num_threads = threads):
    pos1 = 0
    while True:
      white_detect = False
      for lin1 in range(pos1, maxd):
        if entrieview[lin1, col] == WHITE:
          pos1, white_detect = lin1, True
          break
      if not white_detect: break
      pos2 = pos1 + distance
      for lin2 in range(pos2, pos1, -1):
        if entrieview[lin2, col] == WHITE:
          pos2 = lin2 + 1
          break
      for pos in range(pos1, pos2):
        entrieview[pos, col] = BLACK
      pos = (lin1 + lin2) // 2
      entrieview[pos, col] = WHITE
      pos1 = pos2

  return entriecopy

def skeletonize(ndarray entrie, int distance):
  return __skeletonize__(entrie, distance)