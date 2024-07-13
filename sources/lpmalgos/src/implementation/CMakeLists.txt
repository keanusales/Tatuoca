add_library(lpmalgos_base INTERFACE)

set_property(TARGET lpmalgos_base APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
  ${CMAKE_CURRENT_LIST_DIR}
)

add_library(lpmalgos::base ALIAS lpmalgos_base)

hunter_add_package(Eigen)
find_package(Eigen3 CONFIG REQUIRED)

add_library(lpmalgos_impl STATIC
  ellipsoid.cpp
  ellipsoid.h
  machine.cpp
  machine.h
  neighborhood.cpp
  neighborhood.h
  geodesics.cpp
  geodesics.h
)

target_include_directories(lpmalgos_impl PUBLIC ${CMAKE_CURRENT_LIST_DIR})
if(MSVC)
target_compile_definitions(lpmalgos_impl PUBLIC -DGHC_WIN_DISABLE_WSTRING_STORAGE_TYPE)
endif()

target_link_libraries(lpmalgos_impl PUBLIC
  OpenMP::OpenMP_CXX
  lpmalgos::base
  Eigen3::Eigen
  nanoflann
  py::base
)

add_lpmalgos_python_module(lpmalgos
  api_init.cpp
)

target_link_libraries(lpmalgos PUBLIC lpmalgos_impl)