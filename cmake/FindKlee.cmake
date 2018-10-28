cmake_minimum_required(VERSION 3.5)
  include(ExternalProject)
find_package(Git REQUIRED)
# TODO: Fix z3

# set(CMAKE_C_COMPILER ${CLANG_CC})
# set(CMAKE_CXX_COMPILER  ${CLANG_CXX})
ExternalProject_Add( Klee
  PREFIX dependencies/Klee
  DEPENDS STP KleeUCLibC z3Solver
  GIT_REPOSITORY https://github.com/RafaelSa94/klee.git
  GIT_TAG map2check_svcomp2018
  CMAKE_ARGS
     -DENABLE_SOLVER_Z3=ON
     -DZ3_LIBRARIES=${Z3_FOLDER}/lib/libz3.so
     -DZ3_INCLUDE_DIRS=${Z3_FOLDER}/include
     -DENABLE_SOLVER_STP=ON
     -DKLEE_RUNTIME_BUILD_TYPE=Release
     -DENABLE_POSIX_RUNTIME=ON
     -DENABLE_KLEE_UCLIBC=ON
     -DKLEE_UCLIBC_PATH=${KLEE_UCLIB_FOLDER}
     -DCMAKE_BUILD_TYPE=Release
     -DLLVM_CONFIG_BINARY=${LLVM_CONFIG_BIN}
     -DENABLE_TCMALLOC=OFF
     -DENABLE_SYSTEM_TESTS=OFF
     -DENABLE_UNIT_TESTS=OFF
     -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
     -DCMAKE_C_COMPILER=${CLANG_CC}
     -DCMAKE_CXX_COMPILER=${CLANG_CXX}
)