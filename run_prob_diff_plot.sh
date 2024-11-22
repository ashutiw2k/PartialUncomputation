#!/bin/bash

# Define the Python script and output directory
PYTHON_SCRIPT="final_eval_folder/plot_probability_distance.py"
OUTPUT_DIR="final_eval_folder/plots"
CONFIG_PATH="final_eval_folder/configs/config_prob"
OUT_TEXT_FILE="prob_diff_output.txt"

# Function to run Python script with a config file
run_python_script() {
    python3 "$PYTHON_SCRIPT" "$CONFIG_PATH"_"$1".yaml
}

run_for_all_config() {
    # Fork 4 processes and run Python script with different configs
    echo "Running Python Script $PYTHON_SCRIPT for variable ancillas"
    for i in {1..4}; do
        run_python_script "$i"_ancilla &
    done

    wait

    echo "Running Python Script $PYTHON_SCRIPT for variable inputs"
    for i in {1..4}; do
        run_python_script "$i"_input &
    done

    wait

    echo "Running Python Script $PYTHON_SCRIPT for variable gates"
    for i in {1..4}; do
        run_python_script "$i"_gate &
    done

    # Wait for all background processes to finish
    wait

    # Count existing run folders
    run_count=$(find "$OUTPUT_DIR" -maxdepth 1 -type d -name "run_*" | wc -l)

    # Create new run folder
    new_run_folder="$OUTPUT_DIR/run_$((run_count))"
    mkdir -p $new_run_folder

    # Move generated output files to the new folder
    find $OUTPUT_DIR -maxdepth 1 -type f -name "Plot_prob_dist_diff*" -exec mv {} "$new_run_folder" \;

    echo "Script completed. Output files moved to $new_run_folder"
}

> "$OUT_TEXT_FILE"

for j in {1..10}; do
    echo "Run: $j running"
    run_for_all_config >> $OUT_TEXT_FILE 
done