#!/bin/bash
export OMP_WAIT_POLICY=PASSIVE
./build/benchmark --benchmark_out_format=csv --benchmark_out=$1
