import subprocess
import os

def push_files(source_path, dest_path, files, dry_run=False):
    """
    Archives selected files/directories from source to destination using rsync.
    files: list of paths relative to source_path
    """
    if not files:
        return

    # We use --relative to preserve the directory structure
    # e.g. source/Shows/MyShow -> dest/Shows/MyShow
    cmd = [
        "rsync",
        "-avP",
        "--remove-source-files",
        "--relative"
    ]
    
    if dry_run:
        cmd.append("--dry-run")
        
    # Appending files to the command
    cmd.extend(files)
    
    # Destination must be the directory ABOVE where we want to land if using --relative?
    # Actually, with --relative, if we are inside source_path, and we sync "A/B", 
    # and dest is dest_path, it will create dest_path/A/B.
    # So we should run the command from source_path and target dest_path.
    
    cmd.append(dest_path)
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, env=os.environ, cwd=source_path)
        
        # Cleanup empty directories in source
        if not dry_run:
            cleanup_empty_dirs(source_path)
            
    except subprocess.CalledProcessError as e:
        print(f"Error during rsync: {e}")
        # In TUI we might want to catch this to show a popup

def link_files(source_path, dest_path, files):
    """
    Creates symlinks in dest_path for selected files/directories from source_path.
    files: list of paths relative to source_path
    """
    if not files:
        return

    for rel_path in files:
        src = os.path.join(source_path, rel_path)
        dst = os.path.join(dest_path, rel_path)

        # Create parent directories if needed
        parent = os.path.dirname(dst)
        if parent:
            os.makedirs(parent, exist_ok=True)

        if os.path.islink(dst):
            os.unlink(dst)
        elif os.path.exists(dst):
            print(f"Warning: {dst} already exists and is not a symlink, skipping.")
            continue

        try:
            os.symlink(src, dst)
            print(f"Linked: {dst} -> {src}")
        except OSError as e:
            print(f"Error creating symlink {dst}: {e}")


def cleanup_empty_dirs(path):
    """Recursively delete empty directories."""
    # This finds all directories, prints them depth first, and rmdir them. 
    # rmdir only deletes if empty.
    # We use find command for simplicity and robustness or just python walk.
    # "find . -type d -empty -delete" is simplest if available, but let's stick to safe python.
    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            try:
                os.rmdir(os.path.join(root, name))
            except OSError:
                pass # Directory not empty
