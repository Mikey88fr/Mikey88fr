import os
import argparse

def generate_repo_knowledge_file(
    repo_path: str,
    output_dir: str,
    max_output_size_kb: int = 500,  # Max size of the generated MD file per repo in KB
    max_file_size_kb: int = 50,    # Max size of an individual file to include in KB
    include_extensions: list = None,
    exclude_dirs: list = None,
    exclude_files: list = None
):
    """
    Processes a single GitHub repository (local directory) into a concise Markdown knowledge file.

    The knowledge file will contain structured content from selected text-based files,
    prefixed with their relative paths to provide context for an LLM.

    Args:
        repo_path (str): The path to the local GitHub repository directory.
        output_dir (str): The directory where the generated Markdown file will be saved.
        max_output_size_kb (int): The maximum desired size (in KB) of the output Markdown file.
                                   Processing will stop if this limit is reached.
        max_file_size_kb (int): The maximum size (in KB) of an individual file to include.
                                Files larger than this will be skipped.
        include_extensions (list): List of file extensions to include (e.g., ['.py', '.md']).
                                   If None, a default list is used.
        exclude_dirs (list): List of directory names to exclude (e.g., ['.git', 'node_modules']).
                             If None, a default list is used.
        exclude_files (list): List of specific file names to exclude (e.g., ['package-lock.json']).
                              If None, a default list is used.
    """
    if include_extensions is None:
        # Common text/code file extensions to include
        include_extensions = [
            '.txt', '.md', '.markdown', '.rst',  # Documentation
            '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',  # Code & Config
            '.html', '.css', '.scss', '.less', '.xml', '.vue', '.svelte',  # Web
            '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.php', '.sh', '.bash',  # Other languages
            '.rb', '.pl', '.sql', '.csv', '.tsv', '.toml', '.ini', '.cfg', '.conf', # More languages/config
            '.dockerfile', '.Dockerfile', # Docker
            '.env', '.sample', # Environment files (careful with sensitive data)
            '.log', # Logs (potentially large, consider max_file_size_kb)
        ]

    if exclude_dirs is None:
        # Directories to ignore (common build, dependency, or version control folders)
        exclude_dirs = [
            '.git', '.svn', '.hg',  # Version control
            'node_modules', 'bower_components', 'vendor',  # Dependencies
            'build', 'dist', 'out', 'target', '.idea', '.vscode',  # Build/IDE artifacts
            '__pycache__', '.pytest_cache',  # Python specific
            'obj', 'bin', # .NET specific
            'logs', # Large log folders
            'tmp', 'temp' # Temporary files
        ]

    if exclude_files is None:
        # Specific files to ignore (e.g., lock files, large generated files)
        exclude_files = [
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', # JS lock files
            'Pipfile.lock', 'Gemfile.lock', # Python/Ruby lock files
            '.DS_Store', 'Thumbs.db', # OS specific hidden files
            'npm-debug.log', # Node.js debug logs
            'CVS' # Old version control
        ]

    repo_name = os.path.basename(os.path.normpath(repo_path))
    output_filename = os.path.join(output_dir, f"{repo_name}_knowledge.md")
    processed_content = []
    current_size_bytes = 0
    max_output_size_bytes = max_output_size_kb * 1024
    skipped_count = 0
    included_count = 0

    print(f"Processing repository: {repo_name}")

    try:
        # Walk through the repository directory
        for root, dirs, files in os.walk(repo_path, topdown=True):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file_name in files:
                file_ext = os.path.splitext(file_name)[1].lower()
                file_full_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_full_path, repo_path)

                # Skip excluded specific files
                if file_name in exclude_files:
                    skipped_count += 1
                    continue

                # Check file extension
                if file_ext not in include_extensions:
                    skipped_count += 1
                    continue

                # Check file size
                try:
                    file_size_bytes = os.path.getsize(file_full_path)
                    if file_size_bytes > max_file_size_kb * 1024:
                        print(f"  Skipping large file (>{max_file_size_kb}KB): {relative_path}")
                        skipped_count += 1
                        continue
                except OSError:
                    print(f"  Could not get size for file: {relative_path}. Skipping.")
                    skipped_count += 1
                    continue

                # Check if adding this file would exceed the overall output size limit
                # We do a rough estimate based on bytes for efficiency before reading.
                # A more precise check happens after reading.
                if current_size_bytes + file_size_bytes > max_output_size_bytes:
                    print(f"  Max output size reached for {repo_name}. Skipping remaining files.")
                    skipped_count += 1
                    # Set a flag to stop further processing in this repo
                    # by clearing dirs to prevent further os.walk iteration
                    dirs[:] = []
                    break # Break from inner file loop
                
                try:
                    with open(file_full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Add file content with a header
                    file_header = f"## File: {relative_path}\n\n"
                    # Use code block for known code extensions
                    code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',
                                     '.html', '.css', '.scss', '.less', '.java', '.c', '.cpp', '.go', '.rs', '.php',
                                     '.sh', '.bash', '.rb', '.pl', '.sql', '.toml', '.ini', '.cfg', '.conf', 
                                     '.dockerfile', '.Dockerfile']
                    
                    if file_ext in code_extensions:
                        # Remove the leading dot and handle special cases
                        lang = file_ext.lstrip('.')
                        if lang == 'dockerfile':
                            lang = 'dockerfile'
                        elif lang == 'yml':
                            lang = 'yaml'
                        processed_content.append(f"{file_header}```{lang}\n{content}\n```\n\n")
                    else: # For markdown, text, etc., just include content
                        processed_content.append(f"{file_header}{content}\n\n")
                    
                    current_size_bytes = len("".join(processed_content).encode('utf-8'))
                    included_count += 1
                    
                    if current_size_bytes >= max_output_size_bytes:
                        print(f"  Max output size reached ({max_output_size_kb}KB) for {repo_name}. Stopping.")
                        # Clear dirs to prevent further os.walk iteration
                        dirs[:] = []
                        break # Break from inner file loop

                except Exception as e:
                    print(f"  Error reading or processing {relative_path}: {e}. Skipping.")
                    skipped_count += 1
                    continue

            if current_size_bytes >= max_output_size_bytes:
                break # Break from outer directory walk if size limit hit

        # Write the combined content to the output Markdown file
        if processed_content:
            # Add a comprehensive header with repository context
            repo_header = f"""# Repository: {repo_name}

**Repository Type**: GitHub Code Repository  
**Purpose**: Knowledge base for LLM training on {repo_name} codebase  
**Files Included**: {included_count} files  
**Total Size**: ~{current_size_bytes/1024:.1f} KB

## Repository Overview
This knowledge base contains code, documentation, and configuration files from the {repo_name} repository to help understand its structure, patterns, and implementation details.

---

"""
            final_content = repo_header + "".join(processed_content)
            try:
                os.makedirs(output_dir, exist_ok=True)
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                final_size_kb = os.path.getsize(output_filename) / 1024
                print(f"  Successfully created knowledge file: {output_filename} ({final_size_kb:.2f} KB)")
                print(f"  Included {included_count} files, skipped {skipped_count} files.")
            except Exception as e:
                print(f"  Error writing output file {output_filename}: {e}")
        else:
            print(f"  No suitable files found to process for {repo_name}.")

    except Exception as e:
        print(f"An unexpected error occurred while processing {repo_name}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate concise Markdown knowledge files from local GitHub repositories."
    )
    parser.add_argument(
        'source_dir',
        type=str,
        help='The path to the parent directory containing the GitHub repositories (subfolders).'
    )
    parser.add_argument(
        'output_dir',
        type=str,
        help='The directory where the generated Markdown knowledge files will be saved.'
    )
    parser.add_argument(
        '--max_repo_size_kb',
        type=int,
        default=500,
        help='Maximum desired size (in KB) of the output knowledge file per repository. '
             'Defaults to 500 KB.'
    )
    parser.add_argument(
        '--max_file_size_kb',
        type=int,
        default=50,
        help='Maximum size (in KB) of an individual file to include. '
             'Files larger than this will be skipped. Defaults to 50 KB.'
    )
    # You can add more arguments for custom include/exclude lists if needed
    # For now, let's keep it simple and use the defaults within the function.

    args = parser.parse_args()

    if not os.path.isdir(args.source_dir):
        print(f"Error: Source directory '{args.source_dir}' does not exist.")
        return

    os.makedirs(args.output_dir, exist_ok=True) # Ensure output directory exists

    # Iterate through subdirectories, assuming each is a repository
    processed_repos = 0
    print(f"Scanning '{args.source_dir}' for repositories...")
    for item in os.listdir(args.source_dir):
        full_path = os.path.join(args.source_dir, item)
        if os.path.isdir(full_path):
            print(f"\n--- Starting processing for {item} ---")
            generate_repo_knowledge_file(
                repo_path=full_path,
                output_dir=args.output_dir,
                max_output_size_kb=args.max_repo_size_kb,
                max_file_size_kb=args.max_file_size_kb
            )
            processed_repos += 1
            print(f"--- Finished processing for {item} ---\n")

    if processed_repos == 0:
        print(f"No subdirectories (repositories) found in '{args.source_dir}'.")
    else:
        print(f"\n--- All processing complete. {processed_repos} repositories processed. ---")
        print(f"Knowledge files are saved in: {args.output_dir}")

if __name__ == "__main__":
    main()

