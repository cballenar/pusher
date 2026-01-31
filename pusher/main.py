import argparse
import sys
import curses
from pusher.tui import FileBrowser, SOURCE_DIR, DEST_DIR
from pusher.core import push_files

def main():
    parser = argparse.ArgumentParser(description="Archive managed media files.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run of rsync")
    args = parser.parse_args()

    # Ensure source exists (or just let it fail gracefully)
    # in TUI we might handle it
    
    # Run TUI
    # We define a wrapper function to pass to curses.wrapper
    def tui_main(stdscr):
        app = FileBrowser(stdscr)
        return app.run()

    selected_files = curses.wrapper(tui_main)
    
    if selected_files:
        print(f"Pushing {len(selected_files)} items...")
        push_files(SOURCE_DIR, DEST_DIR, selected_files, dry_run=args.dry_run)
        print("Done.")
    else:
        print("No files selected or operation cancelled.")

if __name__ == "__main__":
    main()
