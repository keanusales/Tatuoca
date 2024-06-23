cmake_minimum_required(VERSION 3.16)

if (${CMAKE_VERSION} VERSION_LESS 3.12)
  cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
else()
  cmake_policy(VERSION 3.12)
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

message(STATUS "Generator is set to ${CMAKE_GENERATOR}")
message(STATUS "Project will be built by ${CMAKE_MAKE_PROGRAM}")

include(cmake/package_manager.cmake)

set(CMAKE_CXX_STANDARD 20)

project(
  lpmalgos
  VERSION 1.0.1
  DESCRIPTION "LPM algorithm packages"
  LANGUAGES C CXX)

include("cmake/build_config.cmake")
add_subdirectory(cmake)

set(PROJECT_BASE_DIR ${CMAKE_CURRENT_LIST_DIR})

cmake_policy(SET CMP0069 NEW)
include(CheckIPOSupported)
check_ipo_supported(RESULT is_ipo_supported OUTPUT lto_error)

if (CMAKE_COMPILER_IS_GNUCC AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 10.0
      AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS 12.0)
  # lpmalgos will stackoverflow on gcc 10.x because of IPO, since the inter procedural stuff are too deep.
  message(STATUS "IPO is buggy on GCC-10 and GCC-11, disabling it")
  set(is_ipo_supported OFF)
endif()

if (MSVC)
  set(is_ipo_supported OFF)
  message(STATUS "FIXME: Forcefully disabling LTO because of Visual Studio")
endif()

if (is_ipo_supported AND lpmalgos_USE_IPO)
  set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
  set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_DEBUG OFF)
elseif(lto_error)
  message(WARNING "IPO is not supported: ${lto_error}")
endif()

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(lpmalgos_BUILD_TESTS OFF
    CACHE BOOL "Build unit tests for lpmalgos")

set(PYBIND11_PYTHON_VERSION 3.6
    CACHE STRING "python version")

add_subdirectory(vendor)
add_subdirectory(src)