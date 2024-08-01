import os
import law
import law.contrib
import luigi

from configurator.law_task.param_combination import SrcTask



law.contrib.load("htcondor")
htcondor_dir_name = "htcondor"
src_path = "/afs/cern.ch/user/y/yaskari/cmssw_configurator_project/configurator/law_out/CMSSW_14_1_0_pre4/src"

class HTCondorWorkflow(law.htcondor.HTCondorWorkflow):
    """
    Batch systems are typically very heterogeneous by design, and so is HTCondor. Law does not aim
    to "magically" adapt to all possible HTCondor setups which would certainly end in a mess.
    Therefore we have to configure the base HTCondor workflow in law.contrib.htcondor to work with
    the CERN HTCondor environment. In most cases, like in this example, only a minimal amount of
    configuration is required.
    """

    max_runtime = law.DurationParameter(
        default=3600,
        unit="s",
        significant=False,
        description="maximum runtime; default unit is hours; default: 1",
    )
    poll_interval = law.DurationParameter(
        default=0.5,
        unit="m",
        significant=False,
        description="time between status polls; default unit is minutes; default: 0.5",
    )
    transfer_logs = luigi.BoolParameter(
        default=True,
        significant=False,
        description="transfer job logs to the output directory; default: True",
    )

    htcondor_cpus = luigi.IntParameter(
        default=law.NO_INT,
        significant=False,
        description="number of CPUs to request; empty value leads to the cluster default setting; "
        "no default",
    )

    htcondor_group = luigi.Parameter(
        default=law.NO_STR,
        significant=False,
        description="the name of an accounting group on the cluster to handle user priority; not "
        "used when empty; no default",
    )


    def htcondor_output_directory(self):
        # the directory where submission meta data should be stored
        return law.LocalDirectoryTarget(os.path.join(src_path, htcondor_dir_name))

    # def htcondor_bootstrap_file(self):
    #     # each job can define a bootstrap file that is executed prior to the actual job
    #     # configure it to be shared across jobs and rendered as part of the job itself
    #     bootstrap_file = law.util.rel_path(__file__, "bootstrap.sh")
    #     return law.JobInputFile(bootstrap_file, share=True, render_job=True)

    def htcondor_job_config(self, config, job_num, branches):

        # configure to run in a "el7" container
        # https://batchdocs.web.cern.ch/local/submit.html#os-selection-via-containers
        config.custom_content.append(("MY.WantOS", "el7"))

        # maximum runtime
        config.custom_content.append(("+MaxRuntime", self.max_runtime))

        config.custom_content.append(("RequestCpus", self.htcondor_cpus))

        # copy the entire environment
        config.custom_content.append(("getenv", "true"))


        if self.htcondor_group and self.htcondor_group != law.NO_STR:
            config.custom_content.append(("+AccountingGroup", self.htcondor_group))


        # the CERN htcondor setup requires a "log" config, but we can safely set it to /dev/null
        # if you are interested in the logs of the batch system itself, set a meaningful value here
        log_path = os.path.join(htcondor_dir_name, "logs", "job_{}.log".format(job_num))
        config.custom_content.append(("log", log_path))

        return config

