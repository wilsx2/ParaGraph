#!/bin/bash
export OMP_WAIT_POLICY=PASSIVE
./build/benchmark --benchmark_out=$1 --benchmark_out_format=json
