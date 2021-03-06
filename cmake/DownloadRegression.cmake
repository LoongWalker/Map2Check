set(SVCOMP_BASE "https://raw.githubusercontent.com/sosy-lab/sv-benchmarks/master/c/")
list(APPEND MAP2CHECK_REGRESSION "DEREF")
list(APPEND MAP2CHECK_REGRESSION "FREE")
list(APPEND MAP2CHECK_REGRESSION "MEMTRACK")
list(APPEND MAP2CHECK_REGRESSION "TARGET")
list(APPEND MAP2CHECK_REGRESSION "OVERFLOW")

foreach(R ${MAP2CHECK_REGRESSION})
  include(${PROJECT_SOURCE_DIR}/cmake/DownloadRegression${R}.cmake)
  foreach(F ${MAP2CHECK_REGRESSION_${R}})
    message("Downloading ${F}")
    if(NOT EXISTS ${PROJECT_SOURCE_DIR}/tests/regression/${R}/${F})
      file(DOWNLOAD ${map2check_regression_${F}} ${PROJECT_SOURCE_DIR}/tests/regression/${R}/${F} SHOW_PROGRESS)
    endif()
  endforeach()
endforeach()

#install(DIRECTORY ${PROJECT_BINARY_DIR}/tests/ DESTINATION tests/)
