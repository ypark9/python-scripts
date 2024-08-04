import os
import yaml
import inquirer
import textwrap
import logging
import chardet

logging.basicConfig(level=logging.INFO)

def read_file_content(file_path):
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
        detected = chardet.detect(raw_data)
        if detected['encoding'] is None:
            logging.warning(f"Unable to determine encoding for {file_path}. Skipping.")
            return None
        return raw_data.decode(detected['encoding']).strip()
    except Exception as e:
        logging.warning(f"Error reading file {file_path}: {str(e)}")
        return None

def read_config_file():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_folder, '.repo-crawler-config.json')
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
            return (
                config_data.get("includes", []),
                config_data.get("excludes", []),
                config_data.get("excludes_by_extension", []),
                config_data.get("code_extensions", []),
                config_data.get("no_extension_files", [])
            )
    return [], [], [], [], []

def is_code_file(filename, code_extensions, no_extension_files):
    return any([
        any(filename.endswith(ext) for ext in code_extensions),
        filename in no_extension_files,
        filename.startswith('.') and '.' not in filename[1:]  # Hidden files without extensions
    ])

def walk_repository(repo_path):
    repo_structure = {}
    includes, excludes, excludes_by_extension, code_extensions, no_extension_files = read_config_file()
    
    for root, dirs, files in os.walk(repo_path):
        rel_path = os.path.relpath(root, repo_path)
        path_parts = rel_path.split(os.sep)
        
        logging.info(f"Checking directory: {rel_path}")
        
        # Check if the current directory should be included
        if not any(rel_path.startswith(include) or include in path_parts for include in includes):
            logging.info(f"Skipping directory {rel_path} (not in includes)")
            continue
        
        # Skip directories listed in excludes
        if any(exclude in path_parts for exclude in excludes):
            logging.info(f"Skipping directory {rel_path} (in excludes)")
            continue
        
        current_level = repo_structure
        for part in path_parts:
            if part == '.':
                continue
            current_level = current_level.setdefault(part, {})
        
        for file in files:
            # Skip .DS_Store files
            if file == '.DS_Store':
                logging.info(f"Skipping .DS_Store file in {rel_path}")
                continue
            
            # Skip files with extensions listed in excludes_by_extension
            if any(file.endswith(ext) for ext in excludes_by_extension):
                logging.info(f"Skipping file {file} (excluded extension)")
                continue
            
            if is_code_file(file, code_extensions, no_extension_files):
                file_path = os.path.join(root, file)
                logging.info(f"Reading file: {file_path}")
                content = read_file_content(file_path)
                if content is not None:
                    current_level[file] = content
                    logging.info(f"File content length: {len(content)}")
                else:
                    logging.warning(f"Skipping file {file} (unable to read content)")
            else:
                logging.info(f"Skipping file {file} (not a code file)")
    
    return repo_structure

def get_user_input(prompt, choices):
    questions = [
        inquirer.List('choice',
                      message=prompt,
                      choices=choices,
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers['choice']

def main():
    repo_paths = [
        "/Users/yoonsoopark/Documents/code/bespoke-crm",
        "/Users/yoonsoopark/Documents/code/testing/aws-state-provisioning",
        "/Users/yoonsoopark/Documents/code/python-orgfarm",
        "/Users/yoonsoopark/Documents/code/ncino/hackathon-bespoke",
        "Custom path"
    ]
    output_files = [
        "Use Repository Name",
        "bespoke-crm.yaml",
        "output2.yaml",
        "output3.yaml",
        "Custom filename"
    ]
    
    repo_path = get_user_input("Select the repository path:", repo_paths)
    if repo_path == "Custom path":
        repo_path = input("Enter the custom repository path: ")
    
    output_file = get_user_input("Select the output file name:", output_files)
    if output_file == "Custom filename":
        output_file = input("Enter the custom output file name: ")
    elif output_file == "Use Repository Name":
        output_file = os.path.basename(repo_path) + ".yaml"
    
    repo_structure = walk_repository(repo_path)
    
    with open(output_file, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(repo_structure, yaml_file, default_flow_style=False, allow_unicode=True)
    
    print(f"Repository structure has been written to {output_file}")

if __name__ == "__main__":
    main()