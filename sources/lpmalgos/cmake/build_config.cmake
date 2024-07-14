# USE THIS FILE ONLY FOR GLOBAL SETTINGS OF lpmalgos

include(CheckCXXCompilerFlag)

if (NOT MSVC)
    set(lpmalgos_USE_PCH ON CACHE BOOL "enable PCH")
else()
    set(lpmalgos_USE_PCH OFF)
endif()
set(lpmalgos_STATIC_LIBCPP OFF CACHE BOOL "build libc++ static along with libgomp")
set(lpmalgos_DEBUG_MODE Optimized CACHE STRING "Optimize Debug Mode")
set(lpmalgos_USE_IPO ON CACHE BOOL "make use of interprocedural optimizatin if available")
set_property(CACHE lpmalgos_DEBUG_MODE PROPERTY STRINGS Optimized Non-Optimized)

set(USE_CCACHE ON CACHE BOOL "Use cache to accelerate compile time")
set(lpmalgos_USE_GOLD_LINKER ON CACHE BOOL "Use gold linker")
SET(SANITIZER "" CACHE STRING "sanitizer (address,memory,thread,undefined)")

# Use CMAKE_BUILD_TYPE as a starting point for lpmalgos_BUILD_TYPE
if (NOT DEFINED lpmalgos_BUILD_TYPE)
  if (DEFINED CMAKE_BUILD_TYPE AND "${CMAKE_BUILD_TYPE}")
    message(STATUS "lpmalgos_BUILD_TYPE not set using CMAKE_BUILD_TYPE (${CMAKE_BUILD_TYPE}) initially")
    set(lpmalgos_BUILD_TYPE ${CMAKE_BUILD_TYPE} CACHE STRING "Set lpmalgos build type")
  elseif(MSVC)
    set(lpmalgos_BUILD_TYPE "Release" CACHE STRING "Set lpmalgos build type")
  else()
    set(lpmalgos_BUILD_TYPE "Release" CACHE STRING "Set lpmalgos build type")
  endif()
endif()
if (MSVC)
  set_property(CACHE lpmalgos_BUILD_TYPE PROPERTY STRINGS Release Release)
else()
  set_property(CACHE lpmalgos_BUILD_TYPE PROPERTY STRINGS Release Release)
endif()

option(lpmalgos_BUILD_WHEEL "Build a Python wheel after linking" OFF)

if(MSVC)
  add_compile_options(-utf-8)
  add_compile_options(-bigobj)
endif()

message(STATUS "lpmalgos_BUILD_TYPE is '${lpmalgos_BUILD_TYPE}'")

if (MSVC AND lpmalgos_BUILD_TYPE STREQUAL "Debug")
  message(STATUS "FIXME: Forcing CMAKE_BUILD_TYPE=Release because of MSVC")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
else()
  set(CMAKE_BUILD_TYPE ${lpmalgos_BUILD_TYPE} CACHE STRING "" FORCE)
endif()

message(STATUS "CMAKE_BUILD_TYPE is '${CMAKE_BUILD_TYPE}'")

set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/${lpmalgos_BUILD_TYPE}/)
set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR}/${lpmalgos_BUILD_TYPE}/)

set(lpmalgos_SOURCE_DIR ${PROJECT_SOURCE_DIR})
set(lpmalgos_BINARY_DIR ${PROJECT_BINARY_DIR})
set(lpmalgos_INSTALL_DIR ${PROJECT_BINARY_DIR}/opt)

if(NOT MSVC)
    check_cxx_compiler_flag(-gz CXX_COMPILER_HAS_GZ_FLAG)
endif()

if(APPLE)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -undefined dynamic_lookup")
  set(CMAKE_CXX_FLAGS_DEBUG
      "${CMAKE_CXX_FLAGS_DEBUG} -Og -g  -undefined dynamic_lookup")
  set(CMAKE_CXX_FLAGS_RELEASE
      "${CMAKE_CXX_FLAGS_RELEASE} -O3 -undefined dynamic_lookup")
elseif(UNIX)
  set(CMAKE_CXX_VISIBILITY_PRESET hidden)
  set(CMAKE_C_VISIBILITY_PRESET hidden)
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} -O3")
  if (lpmalgos_DEBUG_MODE STREQUAL "Optimized")
      set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Og -g  -fexceptions")
  else()
      set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g  -fexceptions")
  endif()
endif()

if (SANITIZER STREQUAL "")
  message(STATUS "Sanitizers enabled: (none)")
else()
  message(STATUS "Sanitizers enabled: ${SANITIZER}")
  message(STATUS "GOLD Linker forcefully disabled due to sanitizer use.")
  message(STATUS "To enable again, disable sanitizer then clear the cmake cache")

  set(lpmalgos_USE_GOLD_LINKER OFF)

  if (MSVC)
      add_compile_options(/fsanitize=${SANITIZER} /INCREMENTAL:NO)
      foreach(flag_var
              CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
              CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
              STRING (REGEX REPLACE "[/-]RTC(su|[1su])" "" ${flag_var} "${${flag_var}}")
      endforeach(flag_var)
  else()
      add_compile_options(-g -fsanitize=${SANITIZER} -fno-omit-frame-pointer -fno-optimize-sibling-calls)
      add_link_options(-fsanitize=${SANITIZER})
  endif()
endif()

if(NOT MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden")
  if (lpmalgos_USE_GOLD_LINKER)
      set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fuse-ld=gold")
      set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fuse-ld=gold")
  endif()

  if (lpmalgos_STATIC_LIBCPP)
      set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libstdc++")
      set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libstdc++")
  endif()
endif()

if(USE_CCACHE)
  find_program(CCACHE_FOUND ccache)
  if(CCACHE_FOUND)
    message(STATUS "Using ccache")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
    unset(CCACHE_FOUND CACHE)
  endif(CCACHE_FOUND)
endif()

if(MSVC)
add_definitions(/DBOOST_UUID_FORCE_AUTO_LINK)
endif()

mark_as_advanced(CMAKE_BUILD_TYPE)
mark_as_advanced(CMAKE_INSTALL_PREFIX)
mark_as_advanced(HUNTER_CONFIGURATION_TYPES)
