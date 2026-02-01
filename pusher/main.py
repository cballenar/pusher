import argparse
import sys
import curses
import os
from pusher.tui import FileBrowser, setup_colors
from pusher.core import push_files
from pusher.config import Config

def pick_directory(stdscr, start_path, title):
    browser = FileBrowser(stdscr, root_path=start_path, mode='dir_picker', title_override=title)
    return browser.run()

def draw_header(stdscr, title=""):
    stdscr.clear()
    
    # Ensure colors if we are running in setup before FileBrowser init
    try:
        setup_colors() # Safe to call multiple times? curses.start_color errors if called twice usually
    except curses.error:
        pass # Already started

    H, W = stdscr.getmaxyx()

    # Branding Header
    branding = f" [❯❯] PUSHER {title}"
    branding = branding.ljust(W)
    
    # Use Header Color (Pair 5)
    stdscr.addstr(0, 0, branding, curses.color_pair(5) | curses.A_BOLD)

def draw_footer(stdscr, text):
    H, W = stdscr.getmaxyx()
    # Pad with spaces to full width
    text = text.ljust(W - 1)
    stdscr.addstr(H - 1, 0, text, curses.A_REVERSE)

def run_setup(stdscr, config):
    curses.curs_set(0) # Hide cursor
    H, W = stdscr.getmaxyx()
    
    # Common Layout
    browser_y = 10
    browser_h = H - 10 
    
    # --- PHASE 1: SOURCE DIRECTORY ---
    
    # Initialize Browser for Source (Root, but navigated to Current Dir)
    current_dir = os.getcwd()
    browser = FileBrowser(stdscr, root_path="/", mode='dir_picker', title_override="Select Source Directory", y_offset=browser_y, height=browser_h)
    
    # Navigate browser to current directory relative to root
    # lstrip('/') handles absolute paths transforming to relative for the browser's internal logic
    rel_cwd = current_dir.lstrip('/')
    if rel_cwd:
        browser.current_rel_path = rel_cwd
    else:
        browser.current_rel_path = "."
        
    browser.refresh_file_list()
    
    # Pre-select current directory (rel_cwd)
    # Using "." here only works if browser root is cwd. Since root is /, we need path relative to /.
    # If we are at root, rel_cwd is empty, so use "."
    browser.selected = {rel_cwd} if rel_cwd else {"."}
    
    msg_lines = [
        "First time running the app? Let's get you setup!",
        "",
        "We need to know where your source files are located.",
        "Do you want to use the current directory as the source?",
        "",
        "Press 'c' to Confirm or navigate to your desired location to select it."
    ]
    
    source = None
    while not source:
        draw_header(stdscr)
        for i, line in enumerate(msg_lines):
            stdscr.addstr(2 + i, 2, line)
            
        browser.draw()
        stdscr.refresh()
        
        key = stdscr.getch()
        result = browser.handle_input(key)
        
        if result == "QUIT":
            return False
            
        if result and isinstance(result, str):
            source = result
            
    # --- PHASE 2: TARGET DIRECTORY ---
    
    msg_lines = [
        "Great! Now we need a target directory.",
        "",
        "Where should we push these files to?",
        "",
        "Select a directory below and press 'c' to Confirm."
    ]
    
    # Initialize Browser for Target (Root)
    browser = FileBrowser(stdscr, root_path="/", mode='dir_picker', title_override="Select Target Directory", y_offset=browser_y, height=browser_h)
    
    target = None
    while not target:
        draw_header(stdscr)
        for i, line in enumerate(msg_lines):
            stdscr.addstr(2 + i, 2, line)
            
        browser.draw()
        stdscr.refresh()
        
        key = stdscr.getch()
        result = browser.handle_input(key)
        
        if result == "QUIT":
            return False
            
        if result and isinstance(result, str):
            target = result
                
    config.set("source_dir", source)
    config.set("dest_dir", target)
    return True

def main():
    parser = argparse.ArgumentParser(description="Archive managed media files.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run of rsync")
    parser.add_argument("--config", action="store_true", help="Open configuration menu")
    args = parser.parse_args()

    config = Config()
    
    def tui_entry(stdscr):
        # Check config
        source = config.get("source_dir")
        dest = config.get("dest_dir")
        
        if not source or not dest or args.config:
            if not run_setup(stdscr, config):
                return # User cancelled setup?
            source = config.get("source_dir")
            dest = config.get("dest_dir")
            
        # Common Layout
        H, W = stdscr.getmaxyx()
        browser_y = 10
        browser_h = H - 10
        
        # Main Selection Loop
        app = FileBrowser(stdscr, root_path=source, mode='file_selection', title_override="Select Files", y_offset=browser_y, height=browser_h)
        
        msg_lines = [
            f"Source: {source}",
            f"Target: {dest}",
            "",
            "Select the files or folders you want to push.",
            "Press [Space] to toggle selection, [p] to Push."
        ]
        
        while True:
            draw_header(stdscr)
            for i, line in enumerate(msg_lines):
                if 2 + i < browser_y:
                    stdscr.addstr(2 + i, 2, line)
            
            app.draw()
            stdscr.refresh()
            
            key = stdscr.getch()
            result = app.handle_input(key)
            
            if result == "QUIT":
                return None
                
            if isinstance(result, list):
                return result

    try:
        selected_files = curses.wrapper(tui_entry)
        
        if selected_files:
            source_dir = config.get("source_dir")
            dest_dir = config.get("dest_dir")
            
            print(f"Pushing {len(selected_files)} items from {source_dir} to {dest_dir}...")
            push_files(source_dir, dest_dir, selected_files, dry_run=args.dry_run)
            print("Done.")
        else:
            print("No files selected or operation cancelled.")
            
    except KeyboardInterrupt:
        print("\nCancelled.")

if __name__ == "__main__":
    main()
