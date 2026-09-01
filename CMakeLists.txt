cmake_minimum_required(VERSION 3.18)
project(paragraph LANGUAGES C CXX)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

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

# Debug information
if(CMAKE_BUILD_TYPE STREQUAL "Debug"
OR CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    add_compile_options(
        $<$<COMPILE_LANGUAGE:C>:-pg>
        $<$<COMPILE_LANGUAGE:C>:-fopt-info-vec>
        $<$<COMPILE_LANGUAGE:C>:-fopt-info-vec-missed>
    )
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -pg")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -pg")
endif()

# Packages
find_package(OpenMP REQUIRED)
find_package(MPI REQUIRED COMPONENTS C CXX)
find_package(benchmark REQUIRED)
find_package(Boost REQUIRED)

# ParaGraph
add_library(paragraph SHARED src/paragraph.c)
target_link_libraries(paragraph PRIVATE
    OpenMP::OpenMP_C
#    MPI::MPI_CPP
)

# Benchmark
add_executable(benchmark src/benchmark.cpp)
target_link_libraries(benchmark PRIVATE
    benchmark::benchmark_main
    Boost::boost
    paragraph
)
