from pydantic import ValidationError
import pytest
from configurator.schemas.workflow import Workflow, WorkflowSpecs, Geometry, ProcessModifier

def test_workflow_specs_creation():
    # Test creating a valid WorkflowSpecs instance
    valid_spec = WorkflowSpecs(
        release="CMSSW_12_0_0",
        type="MC",
        era=2021,
        pileup=True,
        geometry=Geometry.D110,
        process_modifier=ProcessModifier.ticl_v3
    )
    assert valid_spec.release == "CMSSW_12_0_0"
    assert valid_spec.type == "MC"
    assert valid_spec.era == 2021
    assert valid_spec.pileup is True
    assert valid_spec.geometry == Geometry.D110.value
    assert valid_spec.process_modifier == ProcessModifier.ticl_v3.value

def test_workflow_specs_with_optional_field():
    # Test creating a WorkflowSpecs instance without the optional process_modifier
    spec_without_modifier = WorkflowSpecs(
        release="CMSSW_12_0_0",
        type="MC",
        era=2021,
        pileup=False,
        geometry=Geometry.D95
    )
    assert spec_without_modifier.process_modifier is None

def test_workflow_specs_with_invalid_geometry():
    # Test creating a WorkflowSpecs instance with an invalid geometry
    with pytest.raises(ValueError):
        WorkflowSpecs(
            release="CMSSW_12_0_0",
            type="MC",
            era=2021,
            pileup=False,
            geometry="InvalidGeometry"  # This should raise a ValueError
        )

def test_workflow_specs_enum_as_string():
    # Test creating a WorkflowSpecs instance using enum value as string
    spec_with_enum_string = WorkflowSpecs(
        release="CMSSW_12_0_0",
        type="MC",
        era=2021,
        pileup=True,
        geometry="D110"  # Assuming your Pydantic model can handle enum names as strings
    )
    assert spec_with_enum_string.geometry == Geometry.D110.value



# Tests
def test_geometry_enum():
    assert Geometry.D86.name == "D86"
    assert Geometry.D86.value == "D86"
    assert Geometry.D114.name == "D114"
    assert Geometry.D114.value == "D114"

def test_process_modifier_enum():
    assert ProcessModifier.ticl_clue3D.name == "ticl_clue3D"
    assert ProcessModifier.ticl_clue3D.value == "ticl_clue3D"
    assert ProcessModifier.ticl_fast_jet.name == "ticl_fast_jet"
    assert ProcessModifier.ticl_fast_jet.value == "ticl_fast_jet"



def test_workflow_specs_with_modifier():
    specs = WorkflowSpecs(
        release="1.0.0",
        type="simulation",
        era=2023,
        pileup=True,
        geometry=Geometry.D86,
        process_modifier=ProcessModifier.ticl_v3
    )
    assert specs.release == "1.0.0"
    assert specs.type == "simulation"
    assert specs.era == 2023
    assert specs.pileup is True
    assert specs.geometry == Geometry.D86.value
    assert specs.process_modifier == ProcessModifier.ticl_v3.value

def test_workflow_specs_invalid_extra_field():
    with pytest.raises(ValidationError):
        WorkflowSpecs(
            release="1.0.0",
            type="simulation",
            era=2023,
            pileup=True,
            geometry=Geometry.D86,
            invalid_field="should_not_be_allowed"
        )

def test_workflow_specs_not_enough_fields():
    with pytest.raises(ValidationError):
        WorkflowSpecs(
            release="1.0.0",
            type="simulation",
        )


def test_workflow_invalid_specs():
    with pytest.raises(ValidationError):
        Workflow(specs="invalid_specs")


def test_workflow_valid_type():
    specs = dict(
        release="1.0.0",
        type="close_by_particle_gun",
        era=2023,
        pileup=True,
        geometry="D86"
    )
    generator = {
        "first_run" : 1,
        "parameters" : {
        "particle_ids" : ["PROTON", "GAMMA"],
        "delta" : 10,
        "flat_pt_generation" : False,
        "eta" : (5, 9),
        }
    }
    workflow = Workflow(specs=specs, generator=generator)
    assert workflow.specs.model_dump(exclude_unset=True) == specs

    gen = workflow.generator.model_dump(exclude_unset=True)
    assert gen == {
        "first_run" : 1,
        "parameters" : {
        "particle_ids" :((2212, 22),),
        "delta" : (10.0,),
        "flat_pt_generation" : (False,),
        "eta" : ((5, 9),),
        }
    }




def test_array_params_generator():
    specs = dict(
        release="1.0.0",
        type="close_by_particle_gun",
        era=2023,
        pileup=True,
        geometry="D86"
    )
    generator = {
        "first_run" : 1,
        "parameters" : {
        "particle_ids" : [["PROTON", "GAMMA"], ["ELECTRON", "POSITRON"]],
        "delta" : [10, 12, 54],
        "flat_pt_generation" : [False, True],
        "eta" : [(5, 9), (3, 7)],
        }
    }
    workflow = Workflow(specs=specs, generator=generator)
    assert workflow.specs.model_dump(exclude_unset=True) == specs
    assert workflow.generator.model_dump(exclude_unset=True) == {
        "first_run" : 1,
        "parameters" : {
        "particle_ids" : ((2212, 22), (-11, 11)),
        "delta" : (10.0, 12.0, 54.0),
        "flat_pt_generation" : (False, True),
        "eta" : ((5.0, 9.0), (3.0, 7.0)),
        }
    }



def test_workflow_invalid_type():
    specs = WorkflowSpecs(
        release="1.0.0",
        type="invalid_type",
        era=2023,
        pileup=True,
        geometry=Geometry.D86
    )
    generator = {
        "first_run" : 1,
        "parameters" : {
        "particle_ids" : ["PROTON", 22],
        "delta" : 10,
        "flat_pt_generation" : False,
        "eta_max" : 9,
        "eta_min" : 5,
        }
    }
    with pytest.raises(ValidationError):
        Workflow(specs=specs, generator=generator)



@pytest.mark.parametrize("generator", [
    {"first_run": 1, "parameters": {"particle_ids": ["INVALID", 22], "delta": 10, "flat_pt_generation": False, "eta_max": 9, "eta_min": 5}},
    "nonsense"
])
def test_workflow_valid_type_invalid_generator(generator):
    specs = WorkflowSpecs(
        release="1.0.0",
        type="close_by_particle_gun",
        era=2023,
        pileup=True,
        geometry=Geometry.D86
    )

    with pytest.raises(ValidationError):
        Workflow(specs=specs, generator=generator)