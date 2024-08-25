#!/usr/bin/env python3

import os
import shutil
import fnmatch
import argparse
import sys

def get_repo_path(default_path):
    user_path = input(f"Enter the path of the repository (default: {default_path}): ").strip()
    return user_path if user_path else default_path

def get_included_folders(repo_path):
    print(f"Available folders in {repo_path}:")
    folders = [f for f in os.listdir(repo_path) if os.path.isdir(os.path.join(repo_path, f))]
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    
    selected = input("Enter the numbers of folders to include (comma-separated) or 'all': ").strip().lower()
    if selected == 'all':
        return folders
    else:
        selected_indices = [int(i.strip()) - 1 for i in selected.split(',') if i.strip().isdigit()]
        return [folders[i] for i in selected_indices if i < len(folders)]

def is_code_file(filename):
    code_extensions = ('.py', '.ts', '.js', '.tf', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs')
    return filename.lower().endswith(code_extensions)

def should_exclude(filename):
    exclude_patterns = ['*.test.*', '*/node_modules/*', '*.spec.*', '*.mock.*', '*/venv/*', '*/env/*', '*.min.js']
    return any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns)

def copy_code_files(src_path, dest_path):
    for root, _, files in os.walk(src_path):
        for file in files:
            src_file = os.path.join(root, file)
            if is_code_file(file) and not should_exclude(src_file):
                rel_path = os.path.relpath(src_file, src_path)
                dest_file = os.path.join(dest_path, rel_path)
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {rel_path}")

def main():
    parser = argparse.ArgumentParser(description="Collect code files from a repository.")
    parser.add_argument("-p", "--path", help="Path to the repository")
    parser.add_argument("-o", "--output", help="Output directory path")
    args = parser.parse_args()

    repo_path = args.path if args.path else get_repo_path(os.getcwd())
    included_folders = get_included_folders(repo_path)
    
    output_path = args.output if args.output else os.path.join(os.getcwd(), 'src')
    os.makedirs(output_path, exist_ok=True)
    
    for folder in included_folders:
        folder_path = os.path.join(repo_path, folder)
        copy_code_files(folder_path, os.path.join(output_path, folder))
    
    print(f"\nCode collection complete. Output is in: {output_path}")

if __name__ == "__main__":
    main()