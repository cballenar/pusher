import curses
import os
import sys
from pusher.core import push_files

# Colors
def setup_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)              # Normal
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN) # Highlight
    curses.init_pair(3, curses.COLOR_GREEN, -1)              # Selected
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)# Selected + Highlight
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header

class FileBrowser:
    def __init__(self, stdscr, root_path, mode='file_selection', title_override=None, y_offset=0, height=None, operation="Push"):
        self.stdscr = stdscr
        self.root_path = os.path.abspath(root_path)
        self.current_rel_path = "."
        self.mode = mode # 'file_selection' or 'dir_picker'
        self.title_override = title_override
        
        self.operation = operation  # "Push" or "Link"
        
        self.y_offset = y_offset
        max_h, max_w = stdscr.getmaxyx()
        self.height = height if height else max_h
        self.width = max_w
        
        self.files = []
        self.selected = set() # Set of paths relative to root_path (only for file_selection)
        self.cursor_idx = 0
        self.offset = 0
        
        # Ensure colors are set up if not already
        if not curses.has_colors():
            setup_colors()
            
        self.refresh_file_list()

    @property
    def current_full_path(self):
         return os.path.abspath(os.path.join(self.root_path, self.current_rel_path))

    def refresh_file_list(self):
        try:
            items = os.listdir(self.current_full_path)
            items.sort()
            
            # Add "." and ".." (Order: .. then .)
            items.insert(0, ".") 
            
            # If not at root, add ..
            if self.current_rel_path != ".":
                items.insert(0, "..")
            
            self.files = items
        except OSError:
            self.files = []
    
    def get_full_rel_path(self, item):
        if self.current_rel_path == ".":
            path = item
        else:
            path = os.path.join(self.current_rel_path, item)
        return os.path.normpath(path)
    
    def draw(self):
        # Header/List/Footer layout logic
        header_y = self.y_offset
        list_y = self.y_offset + 1
        footer_y = self.y_offset + self.height - 1
        
        # Title Logic
        if self.title_override:
            title_text = f" {self.title_override} "
        else:
            title_text = f" {self.current_rel_path} "
        
        # Draw Top Border
        try:
            # Draw line
            self.stdscr.hline(header_y, 0, curses.ACS_HLINE, self.width)
            # Draw corners
            self.stdscr.addch(header_y, 0, curses.ACS_ULCORNER)
            self.stdscr.addch(header_y, self.width - 1, curses.ACS_URCORNER)
            
            # Embed Title
            if len(title_text) < self.width - 4:
                self.stdscr.addstr(header_y, 2, title_text, curses.A_BOLD)
        except curses.error:
            pass

        # List Area
        max_display = self.height - 2 # Header + Footer
        if max_display < 1:
            return 

        for i in range(max_display):
            line_y = list_y + i
            # Clear line first (within borders)
            self.stdscr.move(line_y, 0)
            self.stdscr.clrtoeol()
            
            # Draw side borders
            try:
                self.stdscr.addch(line_y, 0, curses.ACS_VLINE)
                self.stdscr.addch(line_y, self.width - 1, curses.ACS_VLINE)
            except curses.error:
                pass
            
            idx = i + self.offset
            if idx >= len(self.files):
                continue
            
            item = self.files[idx]
            rel_path = self.get_full_rel_path(item)
            full_path_item = os.path.join(self.root_path, rel_path)
            
            is_cursor = (idx == self.cursor_idx)
            is_selected = False
            # Check selection based on RELATIVE path
            if rel_path in self.selected:
                is_selected = True
            
            style = curses.color_pair(1)
            # Highlight cursor row background
            if is_cursor:
                style = curses.color_pair(2)
            
            marker = " "
            if is_selected:
                marker = "*"
                if is_cursor:
                    style = curses.color_pair(4) # Cursor + Selected
                else:
                    style = curses.color_pair(3) # Just Selected
            
            display_name = item
            if item == ".":
                display_name = "./"
            elif item == "..":
                display_name = "../"
            elif os.path.isdir(full_path_item):
                display_name += "/"
                
            line = f" [{marker}] {display_name}"
            # Ensure line fits within borders (start at 1, width-2)
            available_w = self.width - 3 # -1 left border, -1 right border, -1 safety
            line = line[:available_w]
            
            try:
                self.stdscr.addstr(line_y, 1, line, style)
                # If cursor, fill the rest of the line with highlight style (up to right border)
                if is_cursor:
                    fill_len = available_w - len(line)
                    if fill_len > 0:
                        self.stdscr.addstr(line_y, 1 + len(line), " " * fill_len, style)
            except curses.error:
                pass

        # Footer
        if self.mode == 'file_selection':
            footer = " [↑/↓] Navigate  [←/→] In/Out  [Space] Select  [Enter] Confirm  [s] Settings  [q] Quit "
        else:
            footer = " [↑/↓] Navigate  [←/→] In/Out  [Space] Select  [Enter] Confirm  [q] Quit "
        
        # Draw Footer Bar
        # We can draw it as a solid bar, or as the bottom of the box.
        # User liked "framed", so maybe a bottom border?
        # But we need to show keys. 
        # Let's simple format the keys nicely.
        
        # Pad footer
        footer = footer.ljust(self.width - 1) # -1 to avoid bottom-right corner error
        
        try:
             # Draw footer at bottom
             self.stdscr.addstr(footer_y, 0, footer, curses.A_REVERSE)
             # Should we put corners?
             # If the footer is full width reverse, corners might look odd or be overwritten.
             # Let's assume the footer bar acts as the bottom closure visually.
        except curses.error:
            pass

        self.stdscr.refresh()

    def handle_input(self, key):
        if key == ord('q'):
            return "QUIT"
            
        elif key == curses.KEY_UP or key == ord('k'):
            if self.cursor_idx > 0:
                self.cursor_idx -= 1
                if self.cursor_idx < self.offset:
                    self.offset -= 1
        
        elif key == curses.KEY_DOWN or key == ord('j'):
            if self.cursor_idx < len(self.files) - 1:
                self.cursor_idx += 1
                if self.cursor_idx >= self.offset + (self.height - 2): # -2 for header/footer
                    self.offset += 1
        
        elif key == ord(' '): # Space
            item = self.files[self.cursor_idx]
            if item == "..":
                return # Cannot select parent directly
                
            rel_path = self.get_full_rel_path(item)
            
            if self.mode == 'file_selection':
                if rel_path in self.selected:
                    self.selected.remove(rel_path)
                else:
                    self.selected.add(rel_path)
            elif self.mode == 'dir_picker':
                full_path_item = os.path.join(self.root_path, rel_path)
                if os.path.isdir(full_path_item):
                    self.selected = {rel_path}

        elif key == ord('l') or key == curses.KEY_RIGHT: # Right or l (Enter Directory)
            item = self.files[self.cursor_idx]
            rel_path = self.get_full_rel_path(item)
            full_path_item = os.path.join(self.root_path, rel_path)
            
            if item == "..": 
                # Going right on .. doesn't make sense.
                # Let's keep it strict: Right = Go In. 
                pass
            elif item == ".":
                pass 
            elif os.path.isdir(full_path_item):
                self.current_rel_path = rel_path
                self.cursor_idx = 0
                self.offset = 0
                self.refresh_file_list()
        
        elif key in [ord('h'), curses.KEY_BACKSPACE, 127, 8, curses.KEY_LEFT]: # Back
            if self.current_rel_path != ".":
                    self.current_rel_path = os.path.dirname(self.current_rel_path)
                    if not self.current_rel_path:
                        self.current_rel_path = "."
                    self.cursor_idx = 0
                    self.offset = 0
                    self.refresh_file_list()
        
        elif key == 10: # Enter (Confirm/Push)
            # DIR PICKER: Confirm directory
            if self.mode == 'dir_picker':
                 # Explicit selection required.
                 if not self.selected:
                     return None
                     
                 rel = list(self.selected)[0]
                 return os.path.abspath(os.path.join(self.root_path, rel))
            
            # FILE SELECTION: Push
            elif self.mode == 'file_selection':
                if not self.selected:
                    return None
                
                # Show Confirmation Dialog
                confirm_y = self.y_offset + self.height - 2
                try:
                    self.stdscr.addstr(confirm_y, 0, f" {self.operation} selection? (y/N) ".ljust(self.width), curses.color_pair(2))
                    confirm = self.stdscr.getch()
                    if confirm == ord('y'):
                        return list(self.selected)
                except curses.error:
                    pass
                
        elif key == ord('s') and self.mode == 'file_selection':
            return "SETTINGS"

        return None

    def run(self):
        self.refresh_file_list()
        while True:
            self.draw()
            key = self.stdscr.getch()
            result = self.handle_input(key)
            if result == "QUIT":
                return None
            if result is not None:
                return result
