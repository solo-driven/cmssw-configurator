#!/bin/bash

set -e

# Log function
log_info() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - INFO - $1"
}

log_error() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - ERROR - $1" >&2
}

# Start the configuration process
log_info "Starting the configuration process."

# Load the workflow TOML file
if ! conf=$(cat workflow.toml); then
    log_error "Failed to load workflow.toml."
    exit 1
else
    log_info "Successfully loaded workflow.toml."
    echo "$conf" | jq
fi

exit 1


# Parse the TOML file using jq
workflow=$(echo "$conf" | tomli -c)
release=$(echo "$workflow" | jq -r '.workflow.specs.release')

if [ -z "$release" ]; then
    log_error "Release not specified in the TOML file."
    exit 1
fi

root_dir=$(pwd)
CACHE_DIR=".configurator-cache"

release_path="${root_dir}/${release}"

# Create the release if it does not exist
if [ ! -d "$release_path" ]; then
    log_info "Creating release at ${release_path}."
    if ! cmsrel $release; then
        log_error "Error occurred while creating the release."
        exit 1
    fi
else
    log_info "Release directory already exists at ${release_path}."
fi

# Change directory to the release_path/src and set up the environment
cd "${release_path}/src"
log_info "Changed directory to $(pwd)."

source /cvmfs/cms.cern.ch/cmsset_default.sh
source ~/.bashrc
if ! cmsenv; then
    log_error "Failed to execute cmsenv"
    exit 1
else
    log_info "Successfully executed cmsenv"
fi

log_info "Environment setup completed."

# Create cache directory if it does not exist
cache_path="${root_dir}/${CACHE_DIR}"
mkdir -p "$cache_path"
log_info "Cache directory created at ${cache_path}."

cache_release_path="${cache_path}/${release}"
mkdir -p "$cache_release_path"
log_info "Cache release directory created at ${cache_release_path}."

workflows_file="${cache_release_path}/workflows.txt"

# Generate workflows file if it does not exist
if [ ! -f "$workflows_file" ]; then
    log_info "Generating workflows file at ${workflows_file}."
    if ! runTheMatrix.py -w upgrade -n > "$workflows_file"; then
        log_error "Failed to generate workflows file"
        exit 1
    fi
else
    log_info "Workflows file already exists at ${workflows_file}."
fi

# Initialize patterns from the workflow specs
patterns=()

for spec in $(echo "$workflow" | jq -r '.workflow.specs | keys[]'); do
    spec_value=$(echo "$workflow" | jq -r ".workflow.specs.${spec}")
    if [ "$spec" == "type" ]; then
        grep_pattern=$(grep_mapper["type"]["$spec_value"])
        if [ -z "$grep_pattern" ]; then
            log_error "Workflow type '${spec_value}' is not supported."
            exit 1
        fi
        patterns+=("$grep_pattern")
    elif [ "$spec" == "pileup" ]; then
        patterns+=($(grep_mapper["pileup"]["$spec_value"]))
    else
        patterns+=("$spec_value")
    fi
done

# Sort patterns and generate grep command filename
sorted_patterns=$(echo "${patterns[@]}" | tr ' ' '\n' | sort | tr '\n' ' ')
grep_command_filename="grep_${sorted_patterns// /_}.txt"
grep_command_out="${cache_release_path}/${grep_command_filename}"

# Execute grep command and save output if the file does not exist
if [ -f "$grep_command_out" ]; then
    log_info "File ${grep_command_out} exists. Reading as result."
    cat "$grep_command_out"
else
    grep_command="cat ${workflows_file}"
    for pattern in "${patterns[@]}"; do
        grep_command+=" | grep '${pattern}'"
    done

    log_info "Executing command: ${grep_command}"
    if ! eval "$grep_command" > "$grep_command_out"; then
        log_error "Command failed."
        exit 1
    else
        log_info "Command executed successfully. Output saved to file."
        cat "$grep_command_out"
    fi
fi
