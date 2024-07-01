import FWCore.ParameterSet.Config as cms


close_by_particle_gun_attribute_mapping = {
    'add_anti_particle': {'name': 'AddAntiParticle', 'type': cms.bool},
    'verbosity': {'name': 'Verbosity', 'type': cms.untracked.int32},
    'first_run': {'name': 'firstRun', 'type': cms.untracked.uint32},
    'psethack': {'name': 'psethack', 'type': cms.string},
    'parameters': {
        'controlled_by_eta': {'name': 'ControlledByEta', 'type': cms.bool},
        'max_var_spread': {'name': 'MaxVarSpread', 'type': cms.double},
        'delta': {'name': 'Delta', 'type': cms.double},
        'flat_pt_generation': {'name': 'FlatPtGeneration', 'type': cms.bool},
        'phi_max': {'name': 'MaxPhi', 'type': cms.double},
        'phi_min': {'name': 'MinPhi', 'type': cms.double},
        'eta_max': {'name': 'MaxEta', 'type': cms.double},
        'eta_min': {'name': 'MinEta', 'type': cms.double},
        'n_particles': {'name': 'NParticles', 'type': cms.int32},
        'offset_first': {'name': 'OffsetFirst', 'type': cms.bool},
        'overlapping': {'name': 'Overlapping', 'type': cms.bool},
        'particle_ids': {'name': 'PartID', 'type': cms.vint32},
        'pointing': {'name': 'Pointing', 'type': cms.bool},
        'r_max': {'name': 'RMax', 'type': cms.double},
        'r_min': {'name': 'RMin', 'type': cms.double},
        'random_shoot': {'name': 'RandomShoot', 'type': cms.bool},
        't_max': {'name': 'TMax', 'type': cms.double},
        't_min': {'name': 'TMin', 'type': cms.double},
        'use_delta_t': {'name': 'UseDeltaT', 'type': cms.bool},
        'var_max': {'name': 'VarMax', 'type': cms.double},
        'var_min': {'name': 'VarMin', 'type': cms.double},
        'z_max': {'name': 'ZMax', 'type': cms.double},
        'z_min': {'name': 'ZMin', 'type': cms.double},
    }
}




def modify_close_by_particle_gun_generator(generator, params = None, attribute_mapping=close_by_particle_gun_attribute_mapping):
    if params is None:
        params = get_validated_generator_conf()

    for key, value in params.items():
        if key == "parameters":
            for sub_key, sub_value in value.items():
                attr_name, attr_type = attribute_mapping[key][sub_key]['name'], attribute_mapping[key][sub_key]['type']
                setattr(generator.PGunParameters, attr_name, attr_type(sub_value))
        else: 
            attr_name, attr_type  = attribute_mapping[key]['name'], attribute_mapping[key]['type']
            setattr(generator, attr_name, attr_type(value))



# Create a CloseByParticleGun object from the TOML data
def get_validated_generator_conf(toml_file_path: str = "workflow.toml") -> dict:
    from configurator.schemas.generators.close_by_particle_gun import CloseByParticleGun
    import tomli

    with open(toml_file_path, 'rb') as f:
        conf = tomli.load(f)
    generator_conf_data = conf.get("generator")

    if generator_conf_data is not None:
        generator_model = CloseByParticleGun(**generator_conf_data)

        return generator_model.model_dump(exclude_defaults=True)
    else:
        return {}

