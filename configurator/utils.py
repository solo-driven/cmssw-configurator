def generate_dir_name_from_generator_params(params: dict)-> str:
    return "_".join([f"{k}-{v}" for k, v in sorted(params.items())])


from configurator.schemas.particles import PARTICLE_IDS

import subprocess

def run_with_setup(command:str, src_path:str,  from_tar = False, **kwargs) -> subprocess.CompletedProcess:
    """
    A wrapper around subprocess.run to execute a command with a setup command sourced beforehand.

    :param command: The main command to run.
    :param src_path: The path to the source directory.
    :param tar_dir: if src is extracted from tar file, set this to True
    :param kwargs: Additional keyword arguments to pass to subprocess.run.
    :return: The result of subprocess.run.
    """ 
  
    init_command = f"source /cvmfs/cms.cern.ch/cmsset_default.sh && source ~/.bashrc && cmsenv"

    # Combine the setup command with the main command
    full_command = f"cd \"{src_path}\" && {init_command} && {command}"

    print(f"{full_command=}")
    
    # Execute the combined command using subprocess.run
    return subprocess.run(full_command, shell=True,  **kwargs)


shortened_keys = {
        'controlled_by_eta': 'cbe',
        'max_var_spread': 'mvs',
        'delta': 'dlt',
        'flat_pt_generation': 'fpg',
        'pointing': 'ptg',
        'overlapping': 'ovl',
        'random_shoot': 'rds',
        'use_delta_t': 'udt',
        'eta': 'eta',
        'phi': 'phi',
        'r': 'r',
        't': 't',
        'var': 'var',
        'z': 'z',
        'n_particles': 'np',
        'offset_first': 'of',
        'particle_ids': 'pid'
    }

def shorten_key(key):
    """Map full parameter names to their shortened versions."""
    return shortened_keys[key]

def format_value(value):
    """Format the value for inclusion in the directory name."""
    if isinstance(value, bool):
        return 'T' if value else 'F'
    elif isinstance(value, (tuple, list)):
        if isinstance(value[0], float):
            # Note the double braces to include them in the output
            return f"({','.join(f'{v:.2f}' for v in value)})"
        
        return f"({','.join(str(v) for v in value)})"
    elif isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def generate_dir_name(param_dict):
    """Generate a unique and informative directory name from parameters."""

    parts = []
    for k, v in param_dict.items():
        if k == 'particle_ids':
            # Assuming PARTICLE_IDS is accessible and contains the mapping for particle IDs
            particle_parts = f"{shorten_key(k)}_{format_value([PARTICLE_IDS[i] for i in v])}" 

            parts.append(particle_parts)
        else:
            parts.append(f"{shorten_key(k)}_{format_value(v)}")
    dir_name = "_".join(parts)
    # print("dir name is ", dir_name)
    return dir_name


from itertools import product

def get_parameter_combination(parameters: dict):
    keys = list(parameters.keys()) 
    values = parameters.values()
    for value_combination in product(*values):
        yield dict(zip(keys, value_combination))
        
import glob
import os

def get_step1_file(workflow_dir):
    # Construct the search pattern to match all files ending with .py
    search_pattern = os.path.join(workflow_dir, '*.py')
    
    for python_file in glob.glob(search_pattern):
        if not python_file.startswith("step"):
            return python_file
        
    
def get_step_file(step, input_dir):
    """
    Utility function to get the appropriate step file based on the step number.

    :param step: The step number to determine the search pattern.
    :param input_dir: The path to search for the files.
    :return: The path to the appropriate step file.
    """
    # Check the value of step to determine the search pattern
    if step == 1:
        # For step 1, match all .py files
        python_file_pattern = os.path.join(input_dir, '*.py')
        for python_file in glob.glob(python_file_pattern):
            if not os.path.basename(python_file).startswith("step"):
                return python_file
    else:
        # For other steps, match files starting with 'step{step}' and ending with .py
        python_file_pattern = os.path.join(input_dir, f'step{step}*.py')
        for python_file in glob.glob(python_file_pattern):
            return python_file