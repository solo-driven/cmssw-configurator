# import FWCore.ParameterSet.Config as cms


# close_by_particle_gun_attribute_mapping = {
#     'add_anti_particle': {'name': 'AddAntiParticle', 'type': cms.bool},
#     'verbosity': {'name': 'Verbosity', 'type': cms.untracked.int32},
#     'first_run': {'name': 'firstRun', 'type': cms.untracked.uint32},
#     'psethack': {'name': 'psethack', 'type': cms.string},
#     'parameters': {
#         'controlled_by_eta': {'name': 'ControlledByEta', 'type': cms.bool},
#         'max_var_spread': {'name': 'MaxVarSpread', 'type': cms.double},
#         'delta': {'name': 'Delta', 'type': cms.double},
#         'flat_pt_generation': {'name': 'FlatPtGeneration', 'type': cms.bool},
#         'phi_max': {'name': 'MaxPhi', 'type': cms.double},
#         'phi_min': {'name': 'MinPhi', 'type': cms.double},
#         'eta_max': {'name': 'MaxEta', 'type': cms.double},
#         'eta_min': {'name': 'MinEta', 'type': cms.double},
#         'n_particles': {'name': 'NParticles', 'type': cms.int32},
#         'offset_first': {'name': 'OffsetFirst', 'type': cms.bool},
#         'overlapping': {'name': 'Overlapping', 'type': cms.bool},
#         'particle_ids': {'name': 'PartID', 'type': cms.vint32},
#         'pointing': {'name': 'Pointing', 'type': cms.bool},
#         'r_max': {'name': 'RMax', 'type': cms.double},
#         'r_min': {'name': 'RMin', 'type': cms.double},
#         'random_shoot': {'name': 'RandomShoot', 'type': cms.bool},
#         't_max': {'name': 'TMax', 'type': cms.double},
#         't_min': {'name': 'TMin', 'type': cms.double},
#         'use_delta_t': {'name': 'UseDeltaT', 'type': cms.bool},
#         'var_max': {'name': 'VarMax', 'type': cms.double},
#         'var_min': {'name': 'VarMin', 'type': cms.double},
#         'z_max': {'name': 'ZMax', 'type': cms.double},
#         'z_min': {'name': 'ZMin', 'type': cms.double},
#     }
# }

# range_attributes = ['eta', 'phi', 'r', 't', 'var', 'z']


# def close_by_particle_gun_modifier(generator, generator_conf: dict, attribute_mapping=close_by_particle_gun_attribute_mapping):
#     for key, value in generator_conf.items():
#         if key == "parameters":
#             for sub_key, sub_value in value.items():
#                 if sub_key in range_attributes:
#                     for i, postfix in enumerate(("min", "max")):
#                         sub_key_post = f"{sub_key}_{postfix}"
#                         sub_value_post = sub_value[i]

#                         attr_name, attr_type = attribute_mapping[key][sub_key_post]['name'], attribute_mapping[key][sub_key_post]['type']
#                         setattr(generator.PGunParameters, attr_name, attr_type(sub_value_post))
#                 else:
                    
#                     attr_name, attr_type = attribute_mapping[key][sub_key]['name'], attribute_mapping[key][sub_key]['type']
#                     setattr(generator.PGunParameters, attr_name, attr_type(sub_value))
#         else: 
#             attr_name, attr_type  = attribute_mapping[key]['name'], attribute_mapping[key]['type']
#             setattr(generator, attr_name, attr_type(value))




def get_generator_code(generator_attributes: dict):
    params = generator_attributes['parameters']
    repr = f"""
    process.generator = cms.EDProducer("CloseByParticleGunProducer",
        AddAntiParticle = cms.bool({generator_attributes['add_anti_particle']}),
        PGunParameters = cms.PSet(
            ControlledByEta = cms.bool({params['controlled_by_eta']}),
            Delta = cms.double({params['delta']}),
            FlatPtGeneration = cms.bool({params['flat_pt_generation']}),
            MaxVarSpread = cms.bool({params['max_var_spread']}),
            Pointing = cms.bool({params['pointing']}),
            Overlapping = cms.bool({params['overlapping']}),
            RandomShoot = cms.bool({params['random_shoot']}),
            UseDeltaT = cms.bool({params['use_delta_t']}),
            MaxEta = cms.double({params['eta'][1]}),
            MinEta = cms.double({params['eta'][0]}),
            MaxPhi = cms.double({params['phi'][1]}),
            MinPhi = cms.double({params['phi'][0]}),
            RMax = cms.double({params['r'][1]}),
            RMin = cms.double({params['r'][0]}),
            TMax = cms.double({params['t'][1]}),
            TMin = cms.double({params['t'][0]}),
            VarMax = cms.double({params['var'][1]}),
            VarMin = cms.double({params['var'][0]}),
            ZMax = cms.double({params['z'][1]}),
            ZMin = cms.double({params['z'][0]}),
            NParticles = cms.int32({params['n_particles']}),
            OffsetFirst = cms.double({params['offset_first']}),
            PartID = cms.vint32({','.join(map(str, params['particle_ids']))})
        ),
        Verbosity = cms.untracked.int32({generator_attributes['verbosity']}),
        firstRun = cms.untracked.uint32({generator_attributes['first_run']}),
        psethack = cms.string("{generator_attributes['psethack']}")
    )
    """
    import textwrap
    return textwrap.dedent(repr).strip()
