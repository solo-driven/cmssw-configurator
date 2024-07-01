import os
import tomli
import logging
from configurator.workflow_specs_mapper import grep_mapper
import subprocess
from configurator.schemas.workflow import Workflow




def run_with_setup(command:str, **kwargs) -> subprocess.CompletedProcess:
    """
    A wrapper around subprocess.run to execute a command with a setup command sourced beforehand.

    :param command: The main command to run.
    :param kwargs: Additional keyword arguments to pass to subprocess.run.
    :return: The result of subprocess.run.
    """ 
    global src_path

    init_command = f"source /cvmfs/cms.cern.ch/cmsset_default.sh && source ~/.bashrc && cmsenv"
    # Combine the setup command with the main command
    full_command = f"cd \"{src_path}\" && {init_command} && {command}"
    
    # Execute the combined command using subprocess.run
    return subprocess.run(full_command, shell=True,  **kwargs)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting the configuration process.")

try:
    with open("workflow.toml", 'rb') as f:
        conf = tomli.load(f)
       
        import json
        logging.info(json.dumps(conf, indent=4))
        if conf is not None:
            conf = Workflow(**conf).model_dump()
       
    logging.info("Successfully loaded workflow.toml.")
except Exception as e:
    logging.error("Failed to load workflow.toml.", exc_info=True)
    raise


root_dir = os.getcwd()
CACHE_DIR = ".configurator-cache"

# 1. Get the release version
specs: dict = conf.get("specs")
if specs is None:
    logging.error("Workflow specs not specified in the TOML file.")
    raise ValueError("Workflow specs not specified in the TOML file.")

release = specs.pop("release", None)
if release is None:
    logging.error("Release not specified in the TOML file.")
    raise ValueError("Release not specified in the TOML file.")

release_path = os.path.join(root_dir, release)
if not os.path.exists(release_path):
    logging.info(f"Creating release at {release_path}.")
    result = subprocess.run(f"cmsrel {release}", shell=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error occurred while creating the release: {result.stderr}")
        raise Exception(f"Error occurred while creating the release: {result.stderr}")
else:
    logging.info(f"Release directory already exists at {release_path}.")



src_path = os.path.join(release_path, "src")

result = run_with_setup("cmsenv", text=True)

if result.returncode != 0:
    logging.error(f"Failed to execute cmsenv: {result.stderr}")
else:
    logging.info("Successfully executed cmsenv")

logging.info("Environment setup completed.")


# 2. Grepping and 'pulling' the workflow with the specified specs
cache_path = os.path.join(root_dir, CACHE_DIR)
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
    logging.info(f"Cache directory created at {cache_path}.")
else:
    logging.info(f"Cache directory already exists at {cache_path}.")

cache_release_path = os.path.join(cache_path, release)
if not os.path.exists(cache_release_path):
    os.makedirs(cache_release_path)
    logging.info(f"Cache release directory created at {cache_release_path}.")
else:
    logging.info(f"Cache release directory already exists at {cache_release_path}.")

workflows_file = os.path.join(cache_release_path, "workflows.txt")
if not os.path.exists(workflows_file):
    logging.info(f"Generating workflows file at {workflows_file}.")
    # Command to be executed
    command = "runTheMatrix.py -w upgrade -n"

    # Execute the command and capture the output
    result = run_with_setup(command, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        # Write the output to the file if the command was successful
        with open(workflows_file, "w") as file:
            file.write(result.stdout)
    else:
        # Log an error and raise an exception if the command failed
        logging.error(f"Failed to generate workflows file: {result.stderr}")
        raise Exception("Failed to generate workflows file.")
else:
    logging.info(f"Workflows file already exists at {workflows_file}.")

# Initialize a list to hold the patterns
patterns = []

# Populate the patterns list based on the workflow items
for spec, spec_value in specs.items():
    if not spec_value:
        pass

    elif spec == "type":
        if spec_value not in grep_mapper[spec]:
            logging.error(f"Workflow type '{spec_value}' is not supported.")
            raise ValueError(f"Workflow type '{spec_value}' is not supported.")
        patterns.append(grep_mapper[spec][spec_value])
    elif spec == "pileup":
        val = grep_mapper[spec][spec_value]
        patterns.append(grep_mapper[spec][spec_value])

    else:
        patterns.append(spec_value)
logging.info(patterns)
patterns = list(map(str, patterns))
patterns.sort()

# Generate the filename from the sorted patterns
grep_command_filename = "grep_" + "_".join(patterns) + ".txt"
grep_command_out = os.path.join(cache_release_path, grep_command_filename)

# Check if the file exists
if os.path.exists(grep_command_out):
    logging.info(f"File {grep_command_out} exists. Reading as result.")
    with open(grep_command_out, 'r') as file:
        result_content = file.read()
        logging.info(result_content)
else:
    # Create the grep command using the sorted patterns
    grep_command = f"cat {workflows_file}"
    for pattern in patterns:
        if pattern and pattern is not None:
            grep_command += f" | grep '{pattern}'"
    
    result = run_with_setup(grep_command, capture_output=True, text=True)
    if result.returncode == 0:
        if result.stdout == "":
            raise ValueError("No workflows found with the specified specs.")
        
        result_content = str(result.stdout)
        with open(grep_command_out, "w") as file:
            file.write(result_content)
            logging.info("Command executed successfully. Output saved to file.")
        logging.info(result_content)
    else:
        logging.error(f"Command failed: {result.stderr} with code {result.returncode}")
        raise Exception("Failed to execute the command.")

def get_workflow_id(result_content: str) -> str:
    """
    Extract the workflow ID from the result content.

    :param result_content: The content of the result file.
    :return: The workflow ID.
    """
    return result_content.split('\n', maxsplit=1)[0].split(' ', maxsplit=1)[0]

workflow_id = get_workflow_id(result_content)
logging.info(f"Workflow ID: {workflow_id}")

# 3. Pull the workflow
# check if the worklow directory already exists

def get_workflow_dir(workflow_id: str) -> str:
    for dir in os.listdir(src_path):
        if not os.path.isdir(os.path.join(src_path, dir)):
            continue
        
        if workflow_id in dir:
            return os.path.join(src_path, dir)
        
    return ""

workflow_dir = get_workflow_dir(workflow_id)

if not workflow_dir:
    logging.info(f"Pulling the workflow {workflow_id}")
    result = run_with_setup(f"runTheMatrix.py -w upgrade -l {workflow_id} -j 0", text=True, capture_output=True)
    if result.returncode == 0:
        logging.info(result.stdout)
        workflow_dir = get_workflow_dir(workflow_id)
    else:
        logging.error(result.stderr)
        raise Exception("Failed to pull the workflow.")
else:
    logging.info(f"Workflow {workflow_id} already exists in the {workflow_dir}")


# If multiple paramters past ie lists then copy the dir and rename it based on the params 
# 4.1 create workflow files from the list of files






def step0(file_path, generator_code):


    def remove_and_insert_block(file_path, block_start_string, insert_string, rewrite=True, 
                                configurer_start_flag="\n### START ADDED BY CONFIGURATOR ###", 
                                configurer_end_flag="### END ADDED BY CONFIGURATOR ###\n"):
        
        with open(file_path, 'r') as file:
            content = file.read()

        
        # Create the new configuration block with flags
        config_block = f"{configurer_start_flag}\n{insert_string}\n{configurer_end_flag}"
        
        
        # Check if the configurator block already exists
        start_flag_index = content.find(configurer_start_flag)
        end_flag_index = content.find(configurer_end_flag)
        
        if start_flag_index != -1 and end_flag_index != -1:
            if not rewrite:
                print("Configurator block already exists.")
                return

            # Insert the new configuration block at the original block's location
            modified_content = content[:start_flag_index] + config_block + content[end_flag_index + len(configurer_end_flag):]

        else:
            # Find the start of the block
            start_index = content.find(block_start_string) 
            if start_index == -1:
                print(f"Block starting with '{block_start_string}' not found.")
                return
            
            # Count parentheses to find the matching closing one
            open_parentheses = 0
            end_index = -1
            for i, char in enumerate(content[start_index:], start=start_index):
                if char == '(':
                    open_parentheses += 1
                elif char == ')':
                    open_parentheses -= 1
                    if open_parentheses == 0:
                        # Found the matching closing parenthesis
                        end_index = i + 1
                        break
            
            if end_index == -1:
                print("Matching closing parenthesis not found.")
                return
            
            # Insert the new configuration block at the original block's location
            modified_content = content[:start_index] + config_block + content[end_index:]
        
        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(modified_content)

    remove_and_insert_block(file_path, "process.generator", generator_code, rewrite=True)


def get_step0_file(workflow_dir):
    import glob
    # Construct the search pattern to match all files ending with .py
    search_pattern = os.path.join(workflow_dir, '*.py')
    
    for python_file in glob.glob(search_pattern):
        if not python_file.startswith("step"):
            return python_file
    

step0_file = get_step0_file(workflow_dir)

from configurator.modifiers.close_by_particle_gun_modifier import generator_string
if step0_file:
    logging.info(f"Found the step0 file: {step0_file}")
    logging.info("Modifying generator in step0 file.")

    step0(step0_file, generator_string(conf["generator"]))
else:
    logging.error("Could not find the step0 file")