from typing_extensions import Annotated, TypeVar
from pydantic import BaseModel, Discriminator, Field, Tag, ValidationError, ValidationInfo, conlist, model_validator
from typing import Any, List, Optional, Union, Tuple, FrozenSet
from pydantic import field_validator, ConfigDict
from configurator.particles import  Particle, PARTICLES
from pydantic.functional_validators import AfterValidator, BeforeValidator
from typing import Generic, TypeVar, Union,  get_args, get_origin


def is_range(range_):
    assert range_[0] <= range_[1], f"{range_} is not a valid range"
    return range_



Range = Annotated[
    Tuple[float, float],
    AfterValidator(is_range, )
]



def validate_unique_values(vs: tuple):
    seen = set()
    for item in vs:
        if isinstance(item, list):
            item = tuple(item)
        
        if isinstance(item, tuple):
            item = tuple(sorted(item))
        
        assert item not in seen, f"duplicate item {item}"
        seen.add(item)
    return vs


T = TypeVar("T")

def validate_non_empty(values: Tuple[T, ...]):
    if not values:
        raise ValueError("Tuple must contain at least one value.")

    return values
UniqueTuple = Annotated[
    Tuple[T, ...],
    AfterValidator(validate_non_empty),
    AfterValidator(validate_unique_values),
    
]



class TypeChecker(BaseModel, Generic[T]):
        value: T


from typing import Generic, TypeVar, Union,  get_args, get_origin

class SingleOrMultiple(Generic[T]):
    @classmethod
    def __class_getitem__(cls, type_hint) -> Union[
        Annotated[T, Tag("value")], 
        Annotated[UniqueTuple[T], Tag("array")]
    ]:
        def discriminator(vs):
            try:
                origins = []
                for arg in get_args(type_hint):
                    try: 
                        if (origin:=get_origin(arg)) is not None:
                            origins.append(origin)    

                    except Exception as e:
                        pass

                assert len(origins) <= 1, f"Only one type hint is allowed. Unions and ... are not allowed. origins={origins}"

                origin_type = origins[0] if origins else type_hint
                t = TypeChecker[origin_type](value=vs[0]) # raises TypeError if vs is not subscriptable, IndexError if vs is empty
                return "array"
            except (ValidationError, TypeError, IndexError):
                return "value"

        return Annotated[
            Union[
                Annotated[type_hint,  AfterValidator(lambda v: tuple([v])), Tag("value"),], 
                Annotated[UniqueTuple[type_hint], Tag("array")]
            ],
            Discriminator(discriminator=discriminator)
        ]



def get_particle_ids(particle_ids):
    ids = []
    if isinstance(particle_ids[0], tuple):
        for row in particle_ids:
            id_row = []
            for particle in row:
                id_row.append(PARTICLES[particle])
            ids.append(tuple(id_row))
    else:
        for particle in particle_ids:
            ids.append(PARTICLES[particle])
    
    return tuple(ids)




# class ParticleGunParameters(BaseModel):
#     model_config = ConfigDict(extra='forbid', use_enum_values=True)
    
#     controlled_by_eta: SingleOrMultiple[bool] = False
#     max_var_spread: SingleOrMultiple[bool] = None 
#     delta: SingleOrMultiple[float] = None
#     flat_pt_generation: SingleOrMultiple[bool] = None
#     pointing: SingleOrMultiple[bool] = None
#     overlapping: SingleOrMultiple[bool] = None
#     random_shoot: SingleOrMultiple[bool] = None
#     use_delta_t: SingleOrMultiple[bool] = None

#     eta: SingleOrMultiple[Range] = None
#     phi: SingleOrMultiple[Range] = None
#     r: SingleOrMultiple[Range] = None
#     t: SingleOrMultiple[Range] = None
#     var: SingleOrMultiple[Range] = None
#     z: SingleOrMultiple[Range] = None

#     n_particles: SingleOrMultiple[int] = None
#     offset_first: SingleOrMultiple[float] = None

#     particle_ids: Annotated[
#         SingleOrMultiple[UniqueTuple[Particle]],
#         AfterValidator(get_particle_ids)
#     ] = ("GAMMA")



# class CloseByParticleGun(BaseModel):
#     model_config = ConfigDict(extra='forbid')

#     add_anti_particle: Optional[bool] = None
#     verbosity: Optional[int] = None
#     first_run: Optional[int] = None
#     psethack: Optional[str] = None

#     parameters: Optional[ParticleGunParameters] = None



#     def generator_string(self):
#         return f"""
#         process.generator = cms.EDProducer("CloseByParticleGunProducer",
#             AddAntiParticle = cms.bool({self.add_anti_particle}),
#             PGunParameters = cms.PSet(
#                 ControlledByEta = cms.bool({self.parameters.controlled_by_eta}),
#                 Delta = cms.double({self.parameters.delta}),
#                 MaxVarSpread = cms.bool({self.parameters.max_var_spread}),
#                 Pointing = cms.bool({self.parameters.pointing}),
#                 Overlapping = cms.bool({self.parameters.overlapping}),
#                 RandomShoot = cms.bool({self.parameters.random_shoot}),
#                 UseDeltaT = cms.bool({self.parameters.use_delta_t}),
#                 Eta = cms.double({self.parameters.eta}),  # Assuming conversion to double is applicable
#                 Phi = cms.double({self.parameters.phi}),  # Assuming conversion to double is applicable
#                 R = cms.double({self.parameters.r}),  # Assuming conversion to double is applicable
#                 T = cms.double({self.parameters.t}),  # Assuming conversion to double is applicable
#                 Var = cms.double({self.parameters.var}),  # Assuming conversion to double is applicable
#                 Z = cms.double({self.parameters.z}),  # Assuming conversion to double is applicable
#                 NParticles = cms.int32({self.parameters.n_particles}),
#                 OffsetFirst = cms.double({self.parameters.offset_first}),
#                 # Assuming ParticleIDs requires special handling to convert to cms.vint32
#                 PartID = cms.vint32({','.join(map(str, self.parameters.particle_ids))})  
#             ),
#             Verbosity = cms.untracked.int32({self.verbosity}),
#             firstRun = cms.untracked.uint32({self.first_run}),
#             psethack = cms.string("{self.psethack}")
#         )
#         """


class ParticleGunParameters(BaseModel):
    model_config = ConfigDict(extra='forbid', use_enum_values=True)
    
    controlled_by_eta: SingleOrMultiple[bool] = Field(default=True, )
    max_var_spread: SingleOrMultiple[bool] = Field(default=False, )
    delta: SingleOrMultiple[float] = Field(default=10.0, )
    flat_pt_generation: SingleOrMultiple[bool] = Field(default=False, )
    pointing: SingleOrMultiple[bool] = Field(default=True, )
    overlapping: SingleOrMultiple[bool] = Field(default=False, )
    random_shoot: SingleOrMultiple[bool] = Field(default=False, )
    use_delta_t: SingleOrMultiple[bool] = Field(default=False, )

    eta: SingleOrMultiple[Range] = Field(default=(1.7, 2.7), )
    phi: SingleOrMultiple[Range] = Field(default=(-3.14159265359, 3.14159265359), )
    r: SingleOrMultiple[Range] = Field(default=(54.99, 55.01), )
    t: SingleOrMultiple[Range] = Field(default=(0.0, 0.05), )
    var: SingleOrMultiple[Range] = Field(default=(25.0, 200.0), )
    z: SingleOrMultiple[Range] = Field(default=(320.99, 321.01), )

    n_particles: SingleOrMultiple[int] = Field(default=1, )
    offset_first: SingleOrMultiple[float] = Field(default=0.0, )

    particle_ids: Annotated[
        SingleOrMultiple[UniqueTuple[Particle]],
        AfterValidator(get_particle_ids),
    ] = Field(default = ("GAMMA",), )





class CloseByParticleGun(BaseModel):
    model_config = ConfigDict(extra='forbid')

    add_anti_particle: bool = False
    verbosity: int = 0
    first_run: int = 1
    psethack: str = 'random particles in phi and r windows'

    parameters: ParticleGunParameters = Field(default_factory=ParticleGunParameters)

    def generator_string(self):
        params = self.parameters
        repr =  f"""
        process.generator = cms.EDProducer("CloseByParticleGunProducer",
            AddAntiParticle = cms.bool({self.add_anti_particle}),
            PGunParameters = cms.PSet(
                ControlledByEta = cms.bool({params.controlled_by_eta}),
                Delta = cms.double({params.delta}),
                FlatPtGeneration = cms.bool({params.flat_pt_generation}),
                MaxVarSpread = cms.bool({params.max_var_spread}),
                Pointing = cms.bool({params.pointing}),
                Overlapping = cms.bool({params.overlapping}),
                RandomShoot = cms.bool({params.random_shoot}),
                UseDeltaT = cms.bool({params.use_delta_t}),
                MaxEta = cms.double({params.eta[1]}),
                MinEta = cms.double({params.eta[0]}),
                MaxPhi = cms.double({params.phi[1]}),
                MinPhi = cms.double({params.phi[0]}),
                RMax = cms.double({params.r[1]}),
                RMin = cms.double({params.r[0]}),
                TMax = cms.double({params.t[1]}),
                TMin = cms.double({params.t[0]}),
                VarMax = cms.double({params.var[1]}),
                VarMin = cms.double({params.var[0]}),
                ZMax = cms.double({params.z[1]}),
                ZMin = cms.double({params.z[0]}),
                NParticles = cms.int32({params.n_particles}),
                OffsetFirst = cms.double({params.offset_first}),
                PartID = cms.vint32({','.join(map(str, params.particle_ids))})
            ),
            Verbosity = cms.untracked.int32({self.verbosity}),
            firstRun = cms.untracked.uint32({self.first_run}),
            psethack = cms.string("{self.psethack}")
        )
        """
        import textwrap
        return textwrap.dedent(repr).strip()

