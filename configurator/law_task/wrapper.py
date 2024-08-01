import law
import law.contrib
import law.contrib.htcondor


class taskB(law.Task):
    def run(self):
        ...

    def complete(self):
        return False
    

class taskA(law.Task):
    def run(self):
        ...

    def complete(self):
        return True
    

    
class Wrapper(law.WrapperTask, law.contrib.htcondor.HTCondorWorkflow):
    def create_branch_map(self):
        return [1]
    
    def requires(self):
        return [taskA(),   taskB()]