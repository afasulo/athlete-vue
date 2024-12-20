import os
import shutil
from pathlib import Path

def copy_with_path_names(source_dir, dest_dir, max_size_kb=50):
    # Define allowed file extensions
    ALLOWED_EXTENSIONS = ('.py', '.sql', '.html', '.css')
    
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    for root, dirs, files in os.walk(source_path):
        # Skip specified directories
        dirs[:] = [d for d in dirs if d not in ('venv', 'migrations', dest_path.name)]
        
        for file in files:
            # Check if file has any of the allowed extensions
            if not file.lower().endswith(ALLOWED_EXTENSIONS):
                continue
                
            src_file = Path(root) / file
            
            # Skip files larger than max_size_kb
            if src_file.stat().st_size > max_size_kb * 1024:
                print(f"Skipped large file: {src_file}")
                continue
            
            # Create new filename with original path information
            # Create new filename with complete path information
            relative_path = src_file.relative_to(source_path)
            new_filename = "_".join(relative_path.parts)
            dst_file = dest_path / new_filename
            
            # Copy the file with metadata
            shutil.copy2(src_file, dst_file)
            print(f"Copied: {relative_path} -> {new_filename}")

if __name__ == "__main__":
    source_dir = "."
    dest_dir = "./src_files"
    copy_with_path_names(source_dir, dest_dir)