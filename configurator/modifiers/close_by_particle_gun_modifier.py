from textwrap import dedent

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
    
    return dedent(repr).strip()
