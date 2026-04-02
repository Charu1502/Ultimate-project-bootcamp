import os
import shutil
import re
import threading
from tkinter import filedialog
import customtkinter as ctk

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

EXT_MAP = {
    '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images', '.bmp': 'Images', 
    '.tiff': 'Images', '.svg': 'Images', '.pdf': 'PDFs', '.doc': 'Documents', '.docx': 'Documents', 
    '.txt': 'Documents', '.rtf': 'Documents', '.odt': 'Documents', '.xls': 'Spreadsheets', 
    '.xlsx': 'Spreadsheets', '.csv': 'Spreadsheets', '.ods': 'Spreadsheets', '.ppt': 'Presentations', 
    '.pptx': 'Presentations', '.odp': 'Presentations', '.mp4': 'Videos', '.mov': 'Videos', 
    '.avi': 'Videos', '.mkv': 'Videos', '.wmv': 'Videos', '.mp3': 'Audio', '.wav': 'Audio', 
    '.aac': 'Audio', '.flac': 'Audio', '.ogg': 'Audio', '.zip': 'Archives', '.rar': 'Archives', 
    '.tar': 'Archives', '.gz': 'Archives', '.7z': 'Archives', '.exe': 'Executables', 
    '.msi': 'Executables', '.bat': 'Executables', '.sh': 'Executables', '.py': 'Python', 
    '.java': 'Java', '.c': 'C', '.cpp': 'C++', '.html': 'HTML', '.css': 'CSS', '.js': 'JavaScript', 
    '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift', '.go': 'Go', '.rs': 'Rust', '.kt': 'Kotlin', 
    '.dart': 'Dart', '.lua': 'Lua', '.pl': 'Perl', '.r': 'R', '.m': 'MATLAB', '.ps1': 'PowerShell'
}

DUP_PATTERN = re.compile(r'\(\d+\)$')

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Nexus File Operations')
        self.geometry('750x550')
        self.configure(fg_color="#0D0D12") # Deep futuristic dark background

        # Top Frame for Inputs
        self.top_frame = ctk.CTkFrame(self, fg_color="#181824", corner_radius=15)
        self.top_frame.pack(pady=20, padx=20, fill="x")

        self.title_label = ctk.CTkLabel(
            self.top_frame, 
            text='FILE.SYSTEM_ORGANIZER', 
            font=('Consolas', 22, 'bold'), 
            text_color="#00FFCC" # Neon Cyan accent
        )
        self.title_label.pack(pady=(15, 5))

        self.input_frame = ctk.CTkFrame(self.top_frame, fg_color='transparent')
        self.input_frame.pack(pady=10)

        self.entry = ctk.CTkEntry(
            self.input_frame, 
            width=400, 
            placeholder_text='Select target directory...',
            font=('Consolas', 12),
            fg_color="#0D0D12",
            border_color="#00FFCC",
            border_width=1
        )
        self.entry.grid(row=0, column=0, padx=10)

        self.select_btn = ctk.CTkButton(
            self.input_frame, 
            text='BROWSE', 
            font=('Consolas', 12, 'bold'),
            width=100,
            fg_color="#1F51FF", # Neon blue
            hover_color="#0033CC",
            command=self.select_directory
        )
        self.select_btn.grid(row=0, column=1)

        # Action Buttons
        self.action_frame = ctk.CTkFrame(self.top_frame, fg_color='transparent')
        self.action_frame.pack(pady=(5, 15))

        self.org_btn = ctk.CTkButton(
            self.action_frame, 
            text='EXECUTE ORGANIZATION', 
            font=('Consolas', 14, 'bold'),
            fg_color="#00CC66", # Tech green
            hover_color="#00994C",
            command=self.start_organization,
            text_color="#0D0D12"
        )
        self.org_btn.grid(row=0, column=0, padx=10)

        # Integrated Console Output
        self.console_label = ctk.CTkLabel(
            self, 
            text='>_ PROCESS_LOG', 
            font=('Consolas', 14, 'bold'),
            text_color="#A0A0B0"
        )
        self.console_label.pack(anchor="w", padx=25)

        self.console = ctk.CTkTextbox(
            self, 
            width=700, 
            height=250,
            font=('Consolas', 12),
            fg_color="#050508", # Pitch black terminal
            text_color="#00FF00", # Hacker green text
            border_color="#333344",
            border_width=2,
            state="disabled"
        )
        self.console.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        self.is_running = False

    def log_to_console(self, message, message_type="info"):
        """Safely updates the console widget from any thread."""
        self.console.configure(state="normal")
        if message_type == "error":
            prefix = "[ERROR]  "
        elif message_type == "success":
            prefix = "[SUCCESS] "
        elif message_type == "warning":
            prefix = "[WARN]   "
        else:
            prefix = "[INFO]   "

        self.console.insert(ctk.END, f"{prefix}{message}\n")
        self.console.see(ctk.END) # Auto-scroll to bottom
        self.console.configure(state="disabled")

    def select_directory(self):
        if self.is_running:
            return
        path = filedialog.askdirectory()
        if path:
            self.entry.delete(0, ctk.END)
            self.entry.insert(0, path)
            self.log_to_console(f"Target directory set: {path}")

    def start_organization(self):
        dire = self.entry.get().strip()

        if self.is_running:
            self.log_to_console("A process is already running.", "warning")
            return

        if not dire or not os.path.isdir(dire):
            self.log_to_console("Invalid or inaccessible directory path.", "error")
            return

        self.is_running = True
        self.org_btn.configure(state="disabled", fg_color="#555555")
        self.log_to_console(f"Initializing reorganization protocol in {dire}...")

        # Pass control to a background thread
        thread = threading.Thread(target=self._organize_logic, args=(dire,), daemon=True)
        thread.start()

    def _organize_logic(self, dire):
        """Runs strictly in a background thread."""
        fset = set()
        files_moved = 0
        errors = 0

        try:
            with os.scandir(dire) as entries:
                for file in entries:
                    if not file.is_file():
                        continue

                    try:
                        ext = os.path.splitext(file.name)[1].lower()
                        folder = EXT_MAP.get(ext, 'Others')
                        dest_folder_path = os.path.join(dire, folder)

                        if dest_folder_path not in fset:
                            os.makedirs(dest_folder_path, exist_ok=True)
                            fset.add(dest_folder_path)

                        dest_path = os.path.join(dest_folder_path, file.name)

                        # Handle duplicates
                        if os.path.exists(dest_path):
                            base, ext = os.path.splitext(file.name)
                            counter = 1
                            while os.path.exists(dest_path):
                                if DUP_PATTERN.search(base):
                                    base = DUP_PATTERN.sub('', base)
                                dest_path = os.path.join(dest_folder_path, f"{base}({counter}){ext}")
                                counter += 1

                        shutil.move(file.path, dest_path)
                        self.log_to_console(f"Moved: {file.name} -> {folder}/")
                        files_moved += 1

                    except Exception as e:
                        self.log_to_console(f"Failed moving {file.name}: {e}", "error")
                        errors += 1
                        continue

            self.log_to_console(f"Protocol complete. Moved {files_moved} files with {errors} errors.", "success")

        except Exception as e:
            self.log_to_console(f"Fatal directory access error: {e}", "error")

        finally:
            # Re-enable UI components
            self.after(0, self._reset_ui_state)

    def _reset_ui_state(self):
        """Returns the UI to a ready state safely on the main thread."""
        self.is_running = False
        self.org_btn.configure(state="normal", fg_color="#00CC66")


if __name__ == '__main__':
    app = App()
    app.mainloop()