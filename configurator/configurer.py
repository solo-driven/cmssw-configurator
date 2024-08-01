import os
import tomli
import logging
from configurator.workflow_specs_mapper import grep_mapper
import subprocess
from configurator.schemas.workflow import Workflow

from configurator.utils import run_with_setup



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting the configuration process.")

try:
    with open("workflow.toml", 'rb') as f:
        conf = tomli.load(f)
       
        import json
        logging.info(json.dumps(conf, indent=4))
        if conf is not None:
            workflow = Workflow(**conf)
            conf = workflow.model_dump()
            # as every value is a list, we take the first element which will then be update by the combination
            set_conf = workflow.model_dump(exclude_unset=True)


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

result = run_with_setup("cmsenv", src_path=src_path, text=True)

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
    result = run_with_setup(command, src_path=src_path, capture_output=True, text=True)

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
    
    result = run_with_setup(grep_command,src_path=src_path, capture_output=True, text=True)
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
    result = run_with_setup(f"runTheMatrix.py -w upgrade -l {workflow_id} -j 0", src_path=src_path, text=True, capture_output=True)
    if result.returncode == 0:
        logging.info(result.stdout)
        workflow_dir = get_workflow_dir(workflow_id)
    else:
        logging.error(result.stderr)
        raise Exception("Failed to pull the workflow.")
else:
    logging.info(f"Workflow {workflow_id} already exists in the {workflow_dir}")





# If multiple paramters past ie lists then copy the dir and rename it based on the params 
# create a dir for each parameter combination
combinations_dir = "combinations"
combinations_dir_path = os.path.join(os.path.dirname(workflow_dir), combinations_dir)
if not os.path.exists(combinations_dir_path):
    os.makedirs(combinations_dir_path)
    logging.info(f"Directory for parameter combinations created at {combinations_dir_path}")
else:
    logging.info(f"Directory for parameter combinations already exists at {combinations_dir_path}")
os.chdir(combinations_dir_path)

# for each parameter combination create its own dir and copy the workflow dir to it
from configurator.utils import get_parameter_combination, generate_dir_name, get_step0_file
import shutil
from configurator.steps import step0

for param_dict in get_parameter_combination(set_conf["generator"]["parameters"]):
    param_dir_path = os.path.join(combinations_dir_path, generate_dir_name(param_dict))

    if not os.path.exists(param_dir_path):
        shutil.copytree(workflow_dir, param_dir_path)
        logging.info(f"Directory for parameter combination created at {param_dir_path}")
    else:
        logging.info(f"Directory for parameter combination already exists at {param_dir_path}")
    
    # Modify the generator in the step0 file
    step0_file = get_step0_file(param_dir_path)

    if not step0_file:
        logging.error("Could not find the step0 file")
        raise FileNotFoundError(f"Could not find the step0 file in {param_dir_path}")
    else:
        logging.info(f"Found the step0 file: {step0_file}")

    logging.info("Modifying generator in step0 file.")
    conf['generator']['parameters'].update(param_dict)

    step0(step0_file, conf['generator'], conf['specs']['type'])
    

    

    

    

    




    

# step0_file = get_step0_file(workflow_dir)

# from configurator.modifiers.close_by_particle_gun_modifier import generator_string
# if step0_file:
#     logging.info(f"Found the step0 file: {step0_file}")
#     logging.info("Modifying generator in step0 file.")

#     step0(step0_file, generator_string(conf["generator"]))
# else:
#     logging.error("Could not find the step0 file")