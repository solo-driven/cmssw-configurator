import pytest
from configurator.schemas.generators.close_by_particle_gun import CloseByParticleGun, ParticleGunParameters
from pydantic import ValidationError


range_attributes = [
    "eta",
    "phi",
    "r",
    "t",
    "var",
    "z",
]

# Test Extra Fields
def test_extra_fields():
    with pytest.raises(ValidationError):
        CloseByParticleGun(unknown_field=True)
        ParticleGunParameters(unknown_field=True)

# Test Optional Fields
def test_optional_fields():
    params = ParticleGunParameters()  # Omit all optional fields
    assert params is not None



# Test min and max boundary conditions
@pytest.mark.parametrize("range_attributes", range_attributes)
@pytest.mark.parametrize("values", [
    (0, 5),  # Valid tuple
    (-5, 5),  # Valid negative min
    (0, 0),  # Min equals max
    [1, 5], # Valid list
    [-5, 5],
    [0, 0]
])
def test_valid_ranges(range_attributes,values ):
    kwargs = {range_attributes: values}
    ParticleGunParameters(**kwargs)


@pytest.mark.parametrize("range_attributes", range_attributes)
@pytest.mark.parametrize("values", [
    [(0, 5), (1 , 5.3), [5.3, 9.00]],  # valid 2d list with tuples
    [(-5, 5), [3, 5.33]],  # Valid negative min
    [(1, 6)], # 2d list with one element
    [[1.354253, 5]],
    [[3.5623, 455.6], [33.4, 552.4]],
])
def test_valid_ranges_list(range_attributes, values):
    kwargs = {range_attributes: values}
    ParticleGunParameters(**kwargs)



@pytest.mark.parametrize("range_attributes", range_attributes)
@pytest.mark.parametrize("invalid_range_value", [
    (5, 0),  # Max less than min
    (10, -10),  # Max less than min with negative max
    (5, 4),  # Max less than min, close values
    (5,),  # Single value tuple
    [3],  # Single value list
    [5, 3],  # List with max less than min,
    [11, -3532]
])
def test_invalid_ranges(range_attributes, invalid_range_value):
    with pytest.raises(ValidationError):
        kwargs = {range_attributes: invalid_range_value}
        ParticleGunParameters(**kwargs)




@pytest.mark.parametrize("range_attributes", range_attributes)
@pytest.mark.parametrize("invalid_range_values", [
    [[10, 5]],  # List with max less than min
    [[5, 3], [8, 6]],  # Multiple lists with max less than min
    [[10, -10]],  # List with max less than min, including negative number
    [[5, 4], [1, 3]],  # List with max less than min, close values
    [(0, 5), (1 , 5.3), [5.3]], # mixed max in 2 idx
])
def test_invalid_ranges_list(range_attributes, invalid_range_values):
    with pytest.raises(ValidationError):
        kwargs = {range_attributes: invalid_range_values}
        ParticleGunParameters(**kwargs)



@pytest.mark.parametrize("range_attributes", range_attributes)
@pytest.mark.parametrize("values", [
    ("not_a_number", 5),  # Non-numeric min
    (0, "not_a_number"),  # Non-numeric max
    ("not_a_number", "also_not_a_number"),  # Both fields incorrect
    (2,) # only one value
])
def test_invalid_ranges_types(range_attributes, values):
    with pytest.raises(ValidationError):
        kwargs = {range_attributes: values}
        ParticleGunParameters(**kwargs)


@pytest.mark.parametrize("range_attributes", range_attributes)
@pytest.mark.parametrize("values", [
    [["not_a_number", 5]],  # List with non-numeric min
    [[0, "not_a_number"]],  # List with non-numeric max
    [["not_a_number", "also_not_a_number"]],  # List with both fields incorrect
    [[5, "not_a_number"], [0, 3]],  # Mixed list with one incorrect type
])
def test_invalid_ranges_list_types(range_attributes, values):
    with pytest.raises(ValidationError):
        kwargs = {range_attributes: values}
        ParticleGunParameters(**kwargs)



@pytest.mark.parametrize("range_attributes", range_attributes)
@pytest.mark.parametrize("repeated_values", [
    [(1, 2), (1, 2)],  # Direct repetition of tuple
    [[1, 2], [1, 2]],  # Direct repetition of list
    [(1, 2), (3, 4), (1, 2)],  # Repetition with another pair in between
    [[1, 2], [3, 4], [1, 2]],  # List form with repetition and another pair
    [(1, 2), [1, 2]],  # Mixed tuple and list repetition
    [[1, 2], (1, 2), [3, 4], (3, 4)],  # Mixed with multiple repetitions
])
def test_invalid_repeated_ranges(range_attributes, repeated_values):
    with pytest.raises(ValidationError):
        kwargs = {range_attributes: repeated_values}
        ParticleGunParameters(**kwargs)


bool_attributes = [
    "controlled_by_eta",
    "max_var_spread",
    "flat_pt_generation",
    "pointing",
    "overlapping",
    "random_shoot",
    "use_delta_t",
]

@pytest.mark.parametrize("bool_attributes", bool_attributes)
@pytest.mark.parametrize("values", [
    True,  # Single bool
    False,  # Single bool
    0, # converts to False
    1, # converts to True
    [True, False],  # List of bools
    (True, False),  # Tuple of bools
    [False],  # Single bool in list
    (False,),  # Single bool in tuple
])
def test_valid_controlled_by_eta(bool_attributes, values):
    kwargs = {bool_attributes: values}
    ParticleGunParameters(**kwargs)


@pytest.mark.parametrize("bool_attributes", bool_attributes)
@pytest.mark.parametrize("values", [
    "not_a_bool",  # String
    123,  # Integer does not convert to True
    'yes', # String does not convert to True
    [True, "maybe"],  # List with a non-bool value
    (False, 123),  # Tuple with a non-bool value
    [],  # Empty list
    (),  # Empty tuple
    [True, False, []],  # List with an empty list inside
    [True, True],
    [False, True, False]
])
def test_invalid_controlled_by_eta(bool_attributes, values):
    with pytest.raises(ValidationError):
        kwargs = {bool_attributes: values}
        ParticleGunParameters(**kwargs)


float_attributes = [
    "delta",
    "offset_first",
]

@pytest.mark.parametrize("float_attributes", float_attributes)
@pytest.mark.parametrize("values", [
    3.14,  # Single float value
    [3.14, 2.71],  # List of float values
    (1.61, 2.71),  # Tuple of float values
    [3.14],  # Single float value in list
    (2.71,),  # Single float value in tuple
])
def test_valid_float_or_collection(float_attributes, values):
    kwargs = {float_attributes: values}
    ParticleGunParameters(**kwargs)

@pytest.mark.parametrize("float_attributes", float_attributes)
@pytest.mark.parametrize("values", [
    "not_a_float",  # String
    [3.14, "not_a_float"],  # List with a non-float value
    (2.71, "also_not_a_float"),  # Tuple with a non-float value
    [3.14, []],  # List with an empty list inside
    (2.71, ()),  # Tuple with an empty tuple inside
    [3.3, 3.3],  # List with repeated float values
])
def test_invalid_float_or_collection(float_attributes, values):
    with pytest.raises(ValidationError):
        kwargs = {float_attributes: values}
        ParticleGunParameters(**kwargs)



@pytest.mark.parametrize("particle_ids", [
    ("PROTON", "NEUTRON", "GAMMA"),  # Tuple of Particles
    ["PROTON", "NEUTRON", "GAMMA"],  # List of Particles
    [("PROTON", "NEUTRON"), ["GAMMA"]],  # 
    [["PROTON", "NEUTRON"], ["GAMMA",]], 
    [("PROTON",), ("NEUTRON", "GAMMA")],  
])
def test_valid_particle_ids(particle_ids):
    kwargs = {"particle_ids": particle_ids}
    ParticleGunParameters(**kwargs)

@pytest.mark.parametrize("particle_ids", [
    "NONE",  # Single string not in Particles
    "PROTON",
    2323,
    ["PROTON", "NONE"],  # List containing an invalid Particle
    ("PROTON", 123),  # Tuple containing an invalid type
    [["PROTON", "NEUTRON"], ["NONE"]],  # Nested list with an invalid Particle
    [("PROTON", "NEUTRON"), ("NONE",)],  # Nested tuple with an invalid Particle
    [("PROTON", "NEUTRON"), ("PROTON", "NONE",)],  # Nested tuple with an invalid Particle
    ("PROTON", "PROTON"),
    ("PROTON", "NEUTRON", "PROTON"),
    [["PROTON"], ["NEUTRON"], ["PROTON"]],
    [[], ()],  # Empty nested structures
    ["PROTON", []],  # Mixed valid Particle and empty list
    ("NEUTRON", ()),  # Mixed valid Particle and empty tuple
])
def test_invalid_particle_ids(particle_ids):
    with pytest.raises(ValidationError):
        kwargs = {"particle_ids": particle_ids}
        ParticleGunParameters(**kwargs)
        