cmake_minimum_required(VERSION 3.18)
project(paragraph LANGUAGES C CXX)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Parallelize
include(ProcessorCount)
ProcessorCount(N_CORES)
if(N_CORES GREATER 0)
    set(CMAKE_BUILD_PARALLEL_LEVEL ${N_CORES})
endif()

# Release optimizations
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()
if(CMAKE_BUILD_TYPE STREQUAL "Release"
OR CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    add_compile_options(
        $<$<COMPILE_LANGUAGE:C>:-O3>
        $<$<COMPILE_LANGUAGE:C>:-funroll-loops>
        $<$<COMPILE_LANGUAGE:C>:-ffast-math>
        $<$<COMPILE_LANGUAGE:C>:-march=native>
        $<$<COMPILE_LANGUAGE:C>:-mtune=native>
    )
endif()

# Packages
find_package(OpenMP REQUIRED)
find_package(MPI REQUIRED COMPONENTS C)

include(FetchContent)
#FetchContent_Declare(
#    library
#    GIT_REPOSITORY https://github.com/user/library.git
#    GIT_TAG vX.X
#)
#FetchContent_MakeAvailable(library)

add_library(paragraph SHARED src/paragraph.c)
target_include_directories(paragraph PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
#target_link_libraries(paragraph PRIVATE
#    OpenMP::OpenMP_CPP
#    MPI::MPI_CPP
#)
add_executable(example src/example.c)
target_link_libraries(example PRIVATE paragraph)
