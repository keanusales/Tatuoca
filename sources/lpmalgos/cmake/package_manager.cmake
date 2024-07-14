option(HUNTER_ENABLED "Enable Hunter package manager support" ON)
if (WIN32)
    set(HUNTER_CONFIGURATION_TYPES "Release" CACHE STRING "Hunter configuration types")
    macro(get_WIN32_WINNT version)
        if (WIN32 AND CMAKE_SYSTEM_VERSION)
            set(ver ${CMAKE_SYSTEM_VERSION})
            string(REPLACE "." "" ver ${ver})
            string(REGEX REPLACE "([0-9])" "0\\1" ver ${ver})

            set(${version} "0x${ver}")
        endif()
    endmacro()
    get_WIN32_WINNT(ver)
    add_definitions(-D_WIN32_WINNT=0x0A00)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    add_definitions(-DNOMINMAX)
endif()
option(HUNTER_ENABLED "Enable Hunter package manager" )
include("cmake/HunterGate.cmake")
include("cmake/helpers.cmake")
HunterGate(
    URL "https://github.com/cpp-pm/hunter/archive/v0.25.6.tar.gz"
    SHA1 "69e4a05bd514bb05cb2c5aa02ce8ac420516aaf7"
)