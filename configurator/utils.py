def generate_dir_name_from_generator_params(params: dict)-> str:
    return "_".join([f"{k}-{v}" for k, v in sorted(params.items())])
