from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, ValidationError, conint, model_validator
from enum import Enum, auto

class Geometry(Enum):
    def _generate_next_value_(name, *args):
        return name
    
    D86 = auto()
    D88 = auto()
    D91 = auto()
    D92 = auto()
    D93 = auto()
    D94 = auto()
    D95 = auto()
    D96 = auto()
    D97 = auto()
    D98 = auto()
    D99 = auto()
    D100 = auto()
    D101 = auto()
    D102 = auto()
    D103 = auto()
    D104 = auto()
    D105 = auto()
    D106 = auto()
    D107 = auto()
    D108 = auto()
    D109 = auto()
    D110 = auto()
    D111 = auto()
    D112 = auto()
    D113 = auto()
    D114 = auto()

class ProcessModifier(Enum):
    def _generate_next_value_(name, *args):
        return name
    
    ticl_clue3D = auto()
    ticl_v3 = auto()
    ticl_fast_jet = auto()


class WorkflowSpecs(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        use_enum_values=True
    )
    
    release: str
    type: str
    era: int
    pileup: bool
    geometry: Geometry
    process_modifier: Optional[ProcessModifier] = None

from pydantic import PositiveInt

class WorkflowParameters(BaseModel):
    max_events: PositiveInt = 10
    n_jobs: PositiveInt = 1
    customize_step3: bool = False


def snake_to_camel(name: str) -> str:
    components = name.split('_')
    return  ''.join(x.title() for x in components)




class Workflow(BaseModel):
    specs: WorkflowSpecs
    parameters: Optional[WorkflowParameters] = None
    generator: Any  # will be further validated

    @model_validator(mode='after')
    def validate_generator(self):  
        import importlib          
        try:
            module = importlib.import_module(f'configurator.schemas.generators.{self.specs.type}')
            generator_schema = getattr(module, f'{snake_to_camel(self.specs.type)}')

            self.generator = generator_schema(**self.generator)
            return self

        except ImportError as e:
            raise ValueError(f"No generator for '{self.specs.type}' fouond (check spelling of the type): {str(e)}")
        
        except TypeError as e:
            raise ValueError(f"Generator should be initially a dictionary: {str(e)}")
        



        