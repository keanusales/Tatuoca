function(lpmalgos_VERSION_GENERATOR REVISION TAG TAG_DATE COMMIT)
    set(TOOLS_DIR "${PROJECT_BASE_DIR}/tools")
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} git_version.py rev
        WORKING_DIRECTORY ${TOOLS_DIR}
        OUTPUT_VARIABLE R_REV
    )

    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} git_version.py tag
        WORKING_DIRECTORY ${TOOLS_DIR}
        OUTPUT_VARIABLE R_TAG
    )

    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} git_version.py tag_date
        WORKING_DIRECTORY ${PROJECT_BASE_DIR}/tools
        OUTPUT_VARIABLE R_TAG_DATE
    )
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} git_version.py commit
        WORKING_DIRECTORY ${PROJECT_BASE_DIR}/tools
        OUTPUT_VARIABLE R_COMMIT
    )

    string(STRIP ${R_REV} O_REV)
    string(STRIP ${R_TAG} O_TAG)
    string(STRIP ${R_TAG_DATE} O_TAG_DATE)
    string(STRIP ${R_COMMIT} O_COMMIT)

    set(${REVISION} ${O_REV} PARENT_SCOPE)
    set(${TAG} ${O_TAG} PARENT_SCOPE)
    set(${TAG_DATE} ${O_TAG_DATE} PARENT_SCOPE)
    set(${COMMIT} ${O_COMMIT} PARENT_SCOPE)

endfunction()
