#!/usr/bin/bash

benchmark_file="benchmark.json"

if [[ ! -e $benchmark_file ]]; then
    pytest . --benchmark-json=$benchmark_file --benchmark-only
fi


command="python3 analyze.py $benchmark_file"

compare=(
    "-s 5 10 15 20 40 80 125 -i 2000 1000 667 500 250 125 80 -m 0.05 -c 0.1"
    "-s 20 -i 500 -m 0.001 0.01 0.025 0.05 0.1 0.25 -c 0.1"
    "-s 20 -i 500 -m 0.05 -c 0 0.01 0.05 0.1 0.25 0.5 0.75"
)

scatter=(
    "-s 80 -i 125 -m 0.05 -c 0.1"
    "-s 20 -i 500 -m 0.05 -c 0.1 --width 15"
    "-s 15 -i 667 -m 0.1 -c 0.05 --width 15"
)

mean_std=(
    "-s 80 -i 125 -m 0.05 -c 0.1"
    "-s 20 -i 500 -m 0.05 -c 0.1 --width 15 --pyplot-kwargs='{\"markersize\": 1.5}'"
    "-s 15 -i 667 -m 0.1 -c 0.05 --width 15 --pyplot-kwargs='{\"markersize\": 1.5}'"
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