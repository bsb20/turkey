cmake_minimum_required (VERSION 3.5)
project (freqmine)

# Set compiler flags
set (CMAKE_BUILD_TYPE Debug)

add_definitions (-DENABLE_THREADS)
add_definitions (-D_OPENMP)

# Get all source files
file (GLOB SOURCE_FILES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} src/**)

# Set target name and source files
add_executable (${PROJECT_NAME}_pthread ${SOURCE_FILES})

find_package (Threads)
find_package (OpenMP)

if (OPENMP_FOUND)
  set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
  set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()
        
target_link_libraries(
    ${PROJECT_NAME}_pthread
    m
    ${CMAKE_THREAD_LIBS_INIT}
)

# add_dependencies (${PROJECT_NAME}_turkey turkey)
