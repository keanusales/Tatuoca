add_subdirectory(pybind11)

unset(PYBIND11_INSTALL CACHE)
unset(PYBIND11_TEST CACHE)
unset(PYBIND11_WERROR CACHE)
unset(USE_PYTHON_INCLUDE_DIR CACHE)
set(PYBIND11_USE_CROSSCOMPILING ON)

add_library(py_base INTERFACE)

target_link_libraries(py_base INTERFACE
  pybind11::module
)
target_include_directories(py_base INTERFACE
  ${PYTHON_INCLUDE_DIRS}
)
if(MSVC)
  target_compile_definitions(py_base INTERFACE 
    RELEASE_PYTHON_IN_DEBUG
  )
else()
  # remove warnings from pybind11 which we have no control to fix the code
  target_compile_options(py_base INTERFACE 
    -Wno-attributes
  )
endif()

add_library(py::base ALIAS py_base)

include_directories(nanoflann/include)
add_library(nanoflann INTERFACE)
target_include_directories(nanoflann INTERFACE nanoflann/include)