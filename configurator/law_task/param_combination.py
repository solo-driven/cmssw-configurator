import logging
import subprocess
import law
import luigi

from configurator.utils import run_with_setup

workspace_dir = "/afs/cern.ch/user/y/yaskari/cmssw_configurator_project/configurator/law_out"
configurator_cache_dir = '/afs/cern.ch/user/y/yaskari/cmssw_configurator_project/configurator/law_out/.configurator-cache'
combinations_dir = 'combinations'

import os



    

class CreateConfiguratorCachDirTask(law.Task):
    def output(self):
        return law.LocalDirectoryTarget(configurator_cache_dir)
    
    def run(self):
        os.makedirs(self.output().path)


class CashReleaseDirTask(law.Task):
    release = law.Parameter(default="CMSSW_14_1_0_pre4")

    def requires(self):
        return CreateConfiguratorCachDirTask.req(self)
    
    def output(self):
        config_dir = self.input().path
        return law.LocalDirectoryTarget(os.path.join(config_dir, self.release))
    
    def run(self):
        os.makedirs(self.output().path)



class GetCmsReleaseTask(law.Task):
    release = law.Parameter(default="CMSSW_14_1_0_pre4")

    def requires(self):
        return CreateConfiguratorCachDirTask.req(self)

    def output(self):
        return law.LocalDirectoryTarget(os.path.join(workspace_dir, self.release))
    
    def run(self):
        result = subprocess.run(f"cd {workspace_dir} && cmsrel {self.release}", shell=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error occurred while creating the release: {result.stderr}")
            raise Exception(f"Error occurred while creating the release: {result.stderr}")


import tarfile

class GetCmsReleaseDirFromTarTask(law.Task):
    tar_file = law.Parameter(default="CMSSW_14_1_0_pre4.tar")


    @property
    def release(self):
        # when extracting the tar file folder with its name will be created
        return  os.path.splitext(os.path.basename(self.tar_file))[0]

    def requires(self):
        return CreateConfiguratorCachDirTask.req(self)

    def output(self):
        out_dir = os.path.join(workspace_dir, self.release)

        return law.LocalDirectoryTarget(out_dir)
    

    def run(self):
        # Ensure the extraction directory exists
        os.makedirs(workspace_dir, exist_ok=True)

        # Unzip the tar file
        with tarfile.open(self.tar_file, 'r:*') as tar_ref:
            tar_ref.extractall(workspace_dir)

        


 
class SrcTask(law.Task):

    tar_file = luigi.PathParameter(default="CMSSW_14_1_0_pre4.tar", exists=True)
    release = law.Parameter(default="CMSSW_14_1_0_pre4")
    

    def subprocess_run(self, command:str, **kwargs):
        from_tar = self.tar_file is not None
        src_path = kwargs.pop("src_path", self.src_path)
        return run_with_setup(command, src_path = src_path, from_tar = from_tar, **kwargs)


    def requires(self):
        self.release = self.release if not self.tar_file else os.path.splitext(os.path.basename(self.tar_file))[0]

        return {
            "cms_release_dir": GetCmsReleaseTask.req(self, release=self.release) \
                if not self.tar_file else GetCmsReleaseDirFromTarTask.req(self, tar_file=self.tar_file),
        }

    @property
    def src_path(self):
        return os.path.join(workspace_dir, self.input()["cms_release_dir"].path, "src")


class CashCMSReleaseWorkflowsTask(SrcTask):
    def requires(self):
        reqs = super().requires()
        reqs.update({
            "cash_release_dir": CashReleaseDirTask.req(self, release=self.release),
        })
        return reqs
    
    def output(self):
        return law.LocalFileTarget(os.path.join(self.input()['cash_release_dir'].path, "workflows.txt"))
    
    def run(self):

        command = "runTheMatrix.py -w upgrade -n"
         
        # Execute the command and capture the output
        result = self.subprocess_run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            # Write the output to the file if the command was successful
            with self.output().open('w') as file:
                file.write(result.stdout)
        else:
            # Log an error and raise an exception if the command failed
            logging.error(f"Failed to generate workflows file: {result.stderr}")
            raise Exception("Failed to generate workflows file.")


class CashSpecifiedWorkflowsTask(SrcTask):
    type = law.Parameter(default="close_by_particle_gun")
    era = luigi.IntParameter(default=2026)
    pileup = luigi.BoolParameter(default=False)
    geometry = law.Parameter(default="D110") 


    def grep_patterns(self):
        from configurator.workflow_specs_mapper import grep_mapper
        specs = {
            "type": self.type,
            "era": self.era,
            "pileup": self.pileup,
            "geometry": self.geometry
        }

        patterns = []
        for spec, spec_value in specs.items():
            if not spec_value:
                pass

            elif spec == "type":
                if spec_value not in grep_mapper[spec]:
                    logging.error(f"Workflow type '{spec_value}' is not supported.")
                    raise ValueError(f"Workflow type '{spec_value}' is not supported.")
                patterns.append(grep_mapper[spec][spec_value])

            elif spec == "pileup":
                patterns.append(grep_mapper[spec][spec_value])

            else:
                patterns.append(spec_value)

        logging.info(patterns)
        patterns = list(map(str, patterns))
        patterns.sort()
        return patterns
    
    def grep_command_out(self):
        return  "grep_" + "_".join(self.grep_patterns()) + ".txt"
    
    def requires(self):
        reqs = super().requires()
        reqs.update({
            "cash_release_workflows": CashCMSReleaseWorkflowsTask.req(self, release=self.release),
            "cash_release_dir": CashReleaseDirTask.req(self, release=self.release),
        })
        return reqs
    
    def output(self):
        return law.LocalFileTarget(os.path.join(self.input()['cash_release_dir'].path, self.grep_command_out()))
    
    def run(self):
        patterns = self.grep_patterns()
        grep_command = f"cat {self.input()['cash_release_workflows'].path}"
        for pattern in patterns:
            if pattern and pattern is not None:
                grep_command += f" | grep '{pattern}'"
        
        result = self.subprocess_run(grep_command, capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout == "":
                raise ValueError("No workflows found with the specified specs.")
            
            result_content = str(result.stdout)

            with self.output().open('w') as file:
                file.write(result_content)
                logging.info("Command executed successfully. Output saved to file.")
            logging.info(result_content)
    
class GetCMSWorkflowTask(SrcTask):
    type = law.Parameter(default="close_by_particle_gun")
    era = luigi.IntParameter(default=2026)
    pileup = luigi.BoolParameter(default=False)
    geometry = law.Parameter(default="D110") 

    workflow_id = None
    
    
    def requires(self):
        reqs = super().requires()
        reqs.update({
            "cash_specified_workflows": CashSpecifiedWorkflowsTask.req(self)
        })
        return reqs
    
    def get_workflow_id(self) -> str:
        """
        Extract the workflow ID from the result content.

        :param result_content: The content of the result file.
        :return: The workflow ID.

        """
        with self.input()['cash_specified_workflows'].open('r') as file:
            for line in file.readlines():
                id_ = line.split(' ', maxsplit=1)[0]
                try:
                    return str(float(id_))
                except ValueError:
                    continue

        raise ValueError("Workflow ID not found.")
                

    def get_workflow_dir(self, workflow_id: str) -> str:
        for dir in os.listdir(self.src_path):
            if not os.path.isdir(os.path.join(self.src_path, dir)):
                continue
            
            if workflow_id in dir:
                return os.path.join(self.src_path, dir)
            
        return ""
    
    def complete(self):
        print("#"*100)
        print("running complete of GetCMSWorkflowTask")
        try:
            if not self.workflow_id:
                self.workflow_id = self.get_workflow_id()
        except FileNotFoundError:
            return False

        worklfow_dir = self.get_workflow_dir(self.workflow_id)

        return bool(worklfow_dir)
    
    def output(self):

        if not self.workflow_id:
            self.workflow_id = self.get_workflow_id()

        workflow_dir = self.get_workflow_dir(self.workflow_id)
        if not workflow_dir:
            raise ValueError("Workflow directory not found. This output() should be accessed after `run` method was called.")
        
        return law.LocalDirectoryTarget(workflow_dir)

            
    def run(self):
        if not self.workflow_id:
            self.workflow_id = self.get_workflow_id()

        result = self.subprocess_run(f"runTheMatrix.py -w upgrade -l {self.workflow_id} -j 0", text=True, capture_output=True)
        if result.returncode == 0:
            logging.info(result.stdout)

        else:
            logging.error(result.stderr)
            raise Exception("Failed to pull the workflow.")
    


class CreateCombinationsDirTask(SrcTask):
    def output(self):
        return law.LocalDirectoryTarget(os.path.join(self.src_path, combinations_dir))

    def run(self):
        os.makedirs(self.output().path)
        


class CreateCombinationTask(SrcTask):

    workflow_specs = luigi.DictParameter()
    generator_params = luigi.DictParameter()
    out_dir_name = luigi.Parameter()


    def requires(self):
        reqs = super().requires()
        reqs.update({
            "combinations_dir": CreateCombinationsDirTask.req(self, release=self.workflow_specs['release']),
            "workflow_dir": GetCMSWorkflowTask.req(self, **self.workflow_specs)
        })

        return reqs
    

    def output(self):
        return law.LocalDirectoryTarget(os.path.join(self.input()["combinations_dir"].path, self.out_dir_name))

    def complete(self):
        try:
            out = self.output()
            if not os.path.exists(out.path):
                print("output does not exist")
                return False
            return True
        except (FileNotFoundError, ValueError):
            return False

    def run(self):
        import shutil
        from configurator.steps import step0
        from configurator.utils import get_step1_file
        param_dir_path = self.output().path

        if not os.path.exists(param_dir_path):
            shutil.copytree(self.input()['workflow_dir'].path, param_dir_path)


        step0_file = get_step1_file(param_dir_path)
        step0(step0_file, self.generator_params, self.workflow_specs['type'])



from configurator.law_task.my_htcondor import HTCondorWorkflow


class CMSRunTask(SrcTask,  law.LocalWorkflow):

    workflow_file = luigi.parameter.PathParameter(
        default="/afs/cern.ch/user/y/yaskari/cmssw_configurator_project/workflow.toml",
        exists=True
    )

    n_jobs = luigi.IntParameter(default=4)
    step = luigi.IntParameter(default=1)


    def create_branch_map(self):
        import tomli
        from configurator.schemas.workflow import Workflow

        with self.workflow_file.open('rb') as f:
            conf = tomli.load(f)
        
        if conf is None:
            raise ValueError("Could not load the configuration file.")
        
        workflow = Workflow(**conf)
        conf = workflow.model_dump()
        set_conf = workflow.model_dump(exclude_unset=True)

        from configurator.utils import get_parameter_combination, generate_dir_name

        branches_data = []
        for param_dict in get_parameter_combination(set_conf["generator"]["parameters"]):
            out_dir_name = generate_dir_name(param_dict)
            conf['generator']['parameters'].update(param_dict)

            branches_data.append(dict(
                workflow_specs=set_conf['specs'],
                generator_params=conf['generator'],
                out_dir_name=out_dir_name
            )) 


        return branches_data
    
    def requires(self):
        reqs = super().requires()
        reqs.update({
            "combination_task": CreateCombinationTask.req(self, **self.branch_data)
        })


        if self.step > 1:
            print(f"\n In if statement {self.step=} \n ")

            reqs.update({
                f"step_{self.step}_task": CMSRunTask.req(self, step=self.step - 1)
            })

        return reqs
    

    step = luigi.IntParameter(default=1)
    workaround_is_complete = False


    def output(self):
        combination_task_dir_name = os.path.basename(self.input()['combination_task'].path)
        return law.LocalFileTarget(os.path.join(self.src_path, "roots", combination_task_dir_name,  f"step{self.step}.root"))
    
    def complete(self):
        try:
            out = self.output()
            if not os.path.exists(out.path):
                return False
            return True
        except (FileNotFoundError, ValueError):
            return False
        
    def workflow_complete(self):
        return self.workaround_is_complete
    

    def get_step_file(self):
        i = self.input()['combination_task']
        import glob

        # Check the value of self.step to determine the search pattern
        if self.step == 1:
            # For step 1, match all .py files
            python_file_pattern = os.path.join(i.path, '*.py')
            for python_file in glob.glob(python_file_pattern):
                if not python_file.startswith("step"):
                    return python_file
        else:
            # For other steps, match files starting with 'step{self.step}' and ending with .py
            python_file_pattern = os.path.join(i.path, f'step{self.step}*.py')
            for python_file in glob.glob(python_file_pattern):
                return python_file


    def run(self):
        dir_to_save_step_root = os.path.dirname(self.output().path)
        
        step_file = self.get_step_file()

        os.makedirs(dir_to_save_step_root, exist_ok=True)

        if self.step == 1:
            command = f"cmsRun {step_file} -n {self.n_jobs} seed=42"
        else:
            command = f"cmsRun {step_file} inputFile={self.input()[f'step_{self.step}_task'].path}  -n {self.n_jobs} seed=42"
        

        out = self.subprocess_run(command, src_path=dir_to_save_step_root, text=True, capture_output=True)

        # error
        if out.returncode != 0:
            self.workaround_is_complete = False
            self.publish_message(f"stderr is:  {out.stderr}")
            raise Exception(f"cmsRun failed. From command {command}")
        else:
            self.publish_message(f"Step {self.step}: {out.stdout}")

        self.workaround_is_complete = True
    

        





    


    

        
       
        

         
        
