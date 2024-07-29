import os
import json

def is_code_file(filename):
    code_extensions = ['.js', '.ts', '.tsx', '.py', '.tf', '.hcl', '.sh', '.bash']
    return any(filename.endswith(ext) for ext in code_extensions)

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_ignores_file():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    ignores_file_path = os.path.join(current_folder, '.crawler-ignores')
    if os.path.exists(ignores_file_path):
        with open(ignores_file_path, 'r', encoding='utf-8') as file:
            ignores_data = json.load(file)
            print('ignores_data:', ignores_data)
            return ignores_data.get("ignores", [])
    return []

def walk_repository(repo_path):
    repo_structure = {}
    ignores = read_ignores_file()

    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        if any(ignored in root for ignored in ignores):
            continue

        current_level = repo_structure
        path_parts = os.path.relpath(root, repo_path).split(os.sep)

        for part in path_parts:
            if part == '.':
                continue
            current_level = current_level.setdefault(part, {})

        for file in files:
            if is_code_file(file):
                file_path = os.path.join(root, file)
                current_level[file] = read_file_content(file_path)

    return repo_structure

def main():
    default_repo_path = "/path/to/frequently/used/repo"
    default_output_file = "output.json"

    repo_path = input(f"Enter the path to the cloned repository [{default_repo_path}]: ") or default_repo_path
    output_file = input(f"Enter the output file name [{default_output_file}]: ") or default_output_file

    repo_structure = walk_repository(repo_path)

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(repo_structure, json_file, indent=2)

    print(f"Repository structure has been written to {output_file}")

if __name__ == "__main__":
    main()