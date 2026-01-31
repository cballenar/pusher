import curses
import os
import sys
from pusher.core import push_files

SOURCE_DIR = "/mnt/D1/Entertainment"
DEST_DIR = "/mnt/B1/Entertainment"

class FileBrowser:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_path = "."
        self.files = []
        self.selected = set() # Set of paths relative to SOURCE_DIR
        self.cursor_idx = 0
        self.offset = 0
        self.height, self.width = stdscr.getmaxyx()
        
        # Colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # Normal
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Highlight
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) # Selected
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN) # Selected + Highlight

    def refresh_file_list(self):
        full_path = os.path.join(SOURCE_DIR, self.current_path)
        try:
            items = os.listdir(full_path)
            items.sort()
            # If not at root, add ..
            if self.current_path != ".":
                items.insert(0, "..")
            self.files = items
        except OSError:
            self.files = []

    def get_full_rel_path(self, item):
        if self.current_path == ".":
            return item
        return os.path.join(self.current_path, item)

    def draw(self):
        self.stdscr.clear()
        
        # Title
        title = f" Pusher: {self.current_path} | Selected: {len(self.selected)} "
        self.stdscr.addstr(0, 0, title, curses.A_BOLD | curses.A_REVERSE)
        
        # List
        max_display = self.height - 4 # Reserve space for header/footer
        
        for i in range(max_display):
            idx = i + self.offset
            if idx >= len(self.files):
                break
            
            item = self.files[idx]
            rel_path = self.get_full_rel_path(item)
            
            # Determine style
            is_cursor = (idx == self.cursor_idx)
            is_selected = (rel_path in self.selected)
            
            style = curses.color_pair(1)
            marker = " "
            
            if is_selected:
                marker = "*"
                style = curses.color_pair(3)
            
            if is_cursor:
                style = curses.color_pair(2)
                if is_selected:
                    style = curses.color_pair(4)
            
            # Format line
            display_name = item
            if item != ".." and os.path.isdir(os.path.join(SOURCE_DIR, rel_path)):
                display_name += "/"
                
            line = f"[{marker}] {display_name}"
            self.stdscr.addstr(i + 1, 0, line[:self.width-1], style)

        # Footer
        footer = " [Space] Select  [Enter] Enter Dir  [p] Push Selected  [q] Quit "
        self.stdscr.addstr(self.height - 1, 0, footer, curses.A_REVERSE)
        
        self.stdscr.refresh()

    def run(self):
        self.refresh_file_list()
        
        while True:
            self.draw()
            key = self.stdscr.getch()
            
            if key == ord('q'):
                break
                
            elif key == curses.KEY_UP or key == ord('k'):
                if self.cursor_idx > 0:
                    self.cursor_idx -= 1
                    if self.cursor_idx < self.offset:
                        self.offset -= 1
            
            elif key == curses.KEY_DOWN or key == ord('j'):
                if self.cursor_idx < len(self.files) - 1:
                    self.cursor_idx += 1
                    if self.cursor_idx >= self.offset + (self.height - 4):
                        self.offset += 1
            
            elif key == ord(' '): # Space to select
                item = self.files[self.cursor_idx]
                if item == "..":
                    continue
                rel_path = self.get_full_rel_path(item)
                
                if rel_path in self.selected:
                    self.selected.remove(rel_path)
                else:
                    self.selected.add(rel_path)
            
            elif key == 10 or key == ord('l'): # Enter or Right (dive in)
                item = self.files[self.cursor_idx]
                rel_path = self.get_full_rel_path(item)
                full_path = os.path.join(SOURCE_DIR, rel_path)
                
                if item == "..":
                    # Go up
                    self.current_path = os.path.dirname(self.current_path)
                    self.cursor_idx = 0
                    self.offset = 0
                    self.refresh_file_list()
                elif os.path.isdir(full_path):
                    # Go into
                    self.current_path = rel_path
                    self.cursor_idx = 0
                    self.offset = 0
                    self.refresh_file_list()
            
            elif key == ord('h'): # Left (go up)
                if self.current_path != ".":
                     self.current_path = os.path.dirname(self.current_path)
                     self.cursor_idx = 0
                     self.offset = 0
                     self.refresh_file_list()
            
            elif key == ord('p'):
                if not self.selected:
                    continue
                
                # Check for confirmation
                self.stdscr.addstr(self.height - 2, 0, " Confirm Push? (y/N) ", curses.color_pair(2))
                confirm = self.stdscr.getch()
                if confirm == ord('y'):
                    return list(self.selected)

        return None

def run_tui():
    return curses.wrapper(FileBrowser(None).run) # Need to wrap properly, see main
