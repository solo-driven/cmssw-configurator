import importlib

def remove_and_insert_block(file_path, block_start_string, insert_string, rewrite=True, 
                                configurer_start_flag="\n### START ADDED BY CONFIGURATOR ###", 
                                configurer_end_flag="### END ADDED BY CONFIGURATOR ###\n"):
        
        with open(file_path, 'r') as file:
            content = file.read()

        
        # Create the new configuration block with flags
        config_block = f"{configurer_start_flag}\n{insert_string}\n{configurer_end_flag}"
        
        
        # Check if the configurator block already exists
        start_flag_index = content.find(configurer_start_flag)
        end_flag_index = content.find(configurer_end_flag)
        
        if start_flag_index != -1 and end_flag_index != -1:
            if not rewrite:
                print("Configurator block already exists.")
                return

            # Insert the new configuration block at the original block's location
            modified_content = content[:start_flag_index] + config_block + content[end_flag_index + len(configurer_end_flag):]

        else:
            # Find the start of the block
            start_index = content.find(block_start_string) 
            if start_index == -1:
                print(f"Block starting with '{block_start_string}' not found.")
                return
            
            # Count parentheses to find the matching closing one
            open_parentheses = 0
            end_index = -1
            for i, char in enumerate(content[start_index:], start=start_index):
                if char == '(':
                    open_parentheses += 1
                elif char == ')':
                    open_parentheses -= 1
                    if open_parentheses == 0:
                        # Found the matching closing parenthesis
                        end_index = i + 1
                        break
            
            if end_index == -1:
                print("Matching closing parenthesis not found.")
                return
            
            # Insert the new configuration block at the original block's location
            modified_content = content[:start_index] + config_block + content[end_index:]
        
        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(modified_content)

def step0(file_path, generator_params: dict, type="close_by_particle_gun"):
    modifier_module = importlib.import_module(f"configurator.modifiers.{type}_modifier")
    get_generator_code = getattr(modifier_module, "get_generator_code")
    
    generator_code = get_generator_code(generator_params)
    remove_and_insert_block(file_path, "process.generator", generator_code, rewrite=True)
