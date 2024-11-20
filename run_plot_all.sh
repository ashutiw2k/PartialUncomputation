#!/bin/bash

# Define the Python script and output directory
PYTHON=".venv/bin/python"
PYTHON_SCRIPT_PROB="final_eval_folder/plot_probability_distance.py"
PYTHON_SCRIPT_NUM="final_eval_folder/plot_num_ancilla_uncomputed.py"
OUTPUT_DIR="final_eval_folder/plots"
CONFIG_PATH_PROB="final_eval_folder/configs/config_prob"
CONFIG_PATH_NUM="final_eval_folder/configs/config_num"
OUT_TEXT_FILE="prob_diff_output.txt"

# Function to run Python script with a config file
run_python_prob_script() {
    $PYTHON "$PYTHON_SCRIPT_PROB" "$CONFIG_PATH_PROB"_"$1".yaml
}
run_python_num_script() {
    $PYTHON "$PYTHON_SCRIPT_NUM" "$CONFIG_PATH_NUM"_"$1".yaml
}

run_for_all_config() {
    # Fork 4 processes and run Python script with different configs
    echo "Running Python Scripts for variable ancillas"
    for i in {1..4}; do
        run_python_prob_script "$i"_ancilla &
        run_python_num_script "$i"_ancilla &        
    done

    wait

    echo "Running Python Scripts for variable inputs"
    for i in {1..4}; do
        run_python_prob_script "$i"_gate &
        run_python_num_script "$i"_gate &
    done

    wait

    echo "Running Python Scripts for variable gates"
    for i in {1..4}; do
        run_python_prob_script "$i"_input &
        run_python_num_script "$i"_input &
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

for j in {1..15}; do
    echo "Run: $j running"
    run_for_all_config >> $OUT_TEXT_FILE 
done