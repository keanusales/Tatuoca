list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include("helpers.cmake")

function (USE_lpmalgos_PCH target pch_lib)
    if(lpmalgos_USE_PCH)
        message("${target} REUSE_FROM ${pch_lib}")
        target_precompile_headers(${target} REUSE_FROM ${pch_lib})
    endif()
endfunction()
