#!/usr/bin/bash

benchmark_file="benchmark.json"

if [[ ! -e $benchmark_file ]]; then
    pytest . --benchmark-json=$benchmark_file
fi


command="python3 analyze.py $benchmark_file"

compare=(
    "-i 500 -m 0.05 -c 0.1"
    "-s 20 -m  0.05 -c 0.1"
    "-s 20 -i 500 -c 0.1"
    "-s 20 -i 500 -m 0.05"
)

scatter=(
    "-s 20 -i 100 -m 0.05 -c 0.1"
    "-s 20 -i 500 -m 0.05 -c 0.1 --width 15"
    "-s 40 -i 500 -m 0.03 -c 0.5 --width 15"
)

mean_std=(
    "-s 20 -i 100 -m 0.05 -c 0.1"
    "-s 20 -i 500 -m 0.05 -c 0.1 --width 15 --pyplot-kwargs='{\"markersize\": 1.5}'"
    "-s 40 -i 500 -m 0.03 -c 0.5 --width 15 --pyplot-kwargs='{\"markersize\": 1.5}'"
)

for params in "${compare[@]}"; do
    to_execute="$command compare $params"
    echo "Executing: $to_execute"
    eval $to_execute
done

for params in "${scatter[@]}"; do
    to_execute="$command scatter $params"
    echo "Executing: $to_execute"
    eval $to_execute
done

for params in "${mean_std[@]}"; do
    to_execute="$command mean-std $params"
    echo "Executing: $to_execute"
    eval $to_execute
done