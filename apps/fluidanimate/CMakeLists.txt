cmake_minimum_required (VERSION 3.5)
project (fluidanimate CXX)

# Set global project finders
set (CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} $ENV{TURKEY_HOME}/cmake)

# Set (CMAKE_C_STANDARD 99)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
set (CMAKE_BUILD_TYPE Debug)

# Find packages
find_package (Threads)
# find_package (TBB)

# Set definitions
add_definitions (-DENABLE_PTHREADS)
add_definitions (-D_GNU_SOURCE)
add_definitions (-D__XOPEN_SOURCE=600)
# add_definitions (-DENABLE_VISUALIZATION)

# Include directories
include_directories (${TURKEY_INCLUDE_DIR})
include_directories (${CMAKE_CURRENT_SOURCE_DIR}/src)
#
# file (GLOB SOURCE_FILES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} src/**)

# Set target name and source files
add_executable (${PROJECT_NAME}_pthread
  ${CMAKE_CURRENT_SOURCE_DIR}/src/pthreads.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/parsec_barrier.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cellpool.cpp
  )
add_executable (${PROJECT_NAME}_turkey
  ${CMAKE_CURRENT_SOURCE_DIR}/src/turkey.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/parsec_barrier.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cellpool.cpp
  )
# add_executable (${PROJECT_NAME}_tbb
# ${CMAKE_CURRENT_SOURCE_DIR}/src/tbb.cpp
# ${CMAKE_CURRENT_SOURCE_DIR}/src/parsec_barrier.cpp
# ${CMAKE_CURRENT_SOURCE_DIR}/src/cellpool.cpp
# )

target_link_libraries(
  ${PROJECT_NAME}_pthread
  glut
  GL
  GLU
  m
  ${CMAKE_THREAD_LIBS_INIT}
  )
target_link_libraries(
  ${PROJECT_NAME}_turkey
  ${TURKEY_LIBRARIES}
  glut
  GL
  GLU
  m
  ${CMAKE_THREAD_LIBS_INIT}
  )
# target_link_libraries(
# ${PROJECT_NAME}_tbb
# tbb
# glut
# GL
# GLU
# m
# ${CMAKE_THREAD_LIBS_INIT}
# )

target_include_directories (${PROJECT_NAME}_turkey PUBLIC ${TURKEY_INCLUDE_DIRS})

add_dependencies (${PROJECT_NAME}_turkey turkey)
