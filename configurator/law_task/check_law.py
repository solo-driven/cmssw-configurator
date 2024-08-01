import law


class FileCreateWithNoOut(law.Task):
    def output(self):
        return law.LocalFileTarget("/afs/cern.ch/user/y/yaskari/cmssw_configurator_project/configurator/law_task/file.txt")
    
    def run(self):
        with open('/afs/cern.ch/user/y/yaskari/cmssw_configurator_project/configurator/law_task/file.txt', 'w') as f:
            f.write("Hello World")
