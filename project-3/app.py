import customtkinter as ctk
import socket
import concurrent.futures
import threading
import time

# --- App Configuration ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PortScannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("CustomTkinter Port Scanner - Version 1.2")
        self.geometry("850x500")
        self.minsize(800, 450)
        
        # Scan Control Flag
        self.is_scanning = False
        self.timeout_val = 0.5

        self.setup_ui()

    def setup_ui(self):
        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_label = ctk.CTkLabel(self, text="[ ] NETWORK PORT SCANNER", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=2, pady=(15, 15))

        # --- Left Panel (Controls) ---
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Target IP
        self.target_label = ctk.CTkLabel(self.left_frame, text="Target IP/Hostname:")
        self.target_label.pack(anchor="w")
        self.target_entry = ctk.CTkEntry(self.left_frame, placeholder_text="e.g., 192.168.1.1 or localhost")
        self.target_entry.pack(fill="x", pady=(0, 15))
        self.target_entry.insert(0, socket.gethostbyname(socket.gethostname())) # Default to local IP

        # Port Range
        self.port_label = ctk.CTkLabel(self.left_frame, text="Port Range:")
        self.port_label.pack(anchor="w")
        
        self.port_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.port_frame.pack(fill="x", pady=(0, 15))
        
        self.start_port = ctk.CTkEntry(self.port_frame, width=80)
        self.start_port.pack(side="left")
        self.start_port.insert(0, "1")
        
        self.to_label = ctk.CTkLabel(self.port_frame, text=" to ")
        self.to_label.pack(side="left", padx=10)
        
        self.end_port = ctk.CTkEntry(self.port_frame, width=80)
        self.end_port.pack(side="left")
        self.end_port.insert(0, "1024")

        # Scan Options (Placeholders for UI fidelity)
        self.options_label = ctk.CTkLabel(self.left_frame, text="Scan Options:")
        self.options_label.pack(anchor="w")
        
        self.options_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(0, 20))
        self.options_frame.grid_columnconfigure((0, 1), weight=1)

        self.cb_common = ctk.CTkCheckBox(self.options_frame, text="Common Ports")
        self.cb_common.grid(row=0, column=0, sticky="w", pady=5)
        self.cb_common.select()
        
        self.cb_os = ctk.CTkCheckBox(self.options_frame, text="Detect OS")
        self.cb_os.grid(row=0, column=1, sticky="w", pady=5)
        
        self.cb_version = ctk.CTkCheckBox(self.options_frame, text="Service Version")
        self.cb_version.grid(row=1, column=0, sticky="w", pady=5)
        
        self.cb_verbose = ctk.CTkCheckBox(self.options_frame, text="Verbose Output")
        self.cb_verbose.grid(row=1, column=1, sticky="w", pady=5)
        self.cb_verbose.select()

        # Buttons
        self.start_btn = ctk.CTkButton(self.left_frame, text="START SCAN", font=ctk.CTkFont(weight="bold"), command=self.start_scan)
        self.start_btn.pack(fill="x", pady=(10, 5))

        self.cancel_btn = ctk.CTkButton(self.left_frame, text="CANCEL SCAN", fg_color="#8b0000", hover_color="#5c0000", font=ctk.CTkFont(weight="bold"), state="disabled", command=self.cancel_scan)
        self.cancel_btn.pack(fill="x", pady=(5, 0))

        # --- Right Panel (Results) ---
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky="nsew")

        self.results_label = ctk.CTkLabel(self.right_frame, text="Scan Results")
        self.results_label.pack(anchor="w")

        self.console = ctk.CTkTextbox(self.right_frame, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#1e1e1e", text_color="#d4d4d4",state="disabled")
        self.console.pack(fill="both", expand=True)

        # --- Status Bar ---
        self.status_var = ctk.StringVar(value="Status: Ready | Threads: 50 | Timeout: 0.5s")
        self.status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", fg_color="#2b2b2b", padx=20)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

    # --- Core Logic Integration ---
    def pscan(self, port, target):
        """Individual port scan logic (adapted from provided script)"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.timeout_val)
            s = sock.connect_ex((target, port))
            if s == 0:
                return True
            else:
                return False

    def log(self, message):
        """Helper to print to the GUI console safely"""
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def start_scan(self):
        if self.is_scanning:
            return

        target = self.target_entry.get().strip()
        try:
            start_p = int(self.start_port.get())
            end_p = int(self.end_port.get())
        except ValueError:
            self.log("[-] Error: Port range must be valid integers.")
            return

        if not target:
            self.log("[-] Error: Target IP cannot be empty.")
            return

        # Update UI state
        self.console.delete("1.0", "end")
        self.is_scanning = True
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.status_var.set(f"Status: Scanning {target}... | Threads: 50 | Timeout: {self.timeout_val}s")

        # Start the background thread so the GUI doesn't freeze
        scan_thread = threading.Thread(target=self.loop, args=(target, start_p, end_p), daemon=True)
        scan_thread.start()

    def cancel_scan(self):
        if self.is_scanning:
            self.is_scanning = False
            self.status_var.set("Status: Cancelling... | Threads: 50 | Timeout: 0.5s")

    def loop(self, target, start_p, end_p):
        """
        Multithreaded port scan on the specified target IP address.
        Adapted from provided logic to include cancellation and GUI updates.
        """
        self.log(f"[+] Scanning {target} (Ports: {start_p}-{end_p})")
        self.log("-" * 55)
        self.log(f"{'PORT':<10} {'STATE':<10} SERVICE")
        
        open_ports_count = 0
        start_time = time.time()

        # Added max_workers to control thread volume and prevent OS errors
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            # Map futures to their respective ports
            futures = {executor.submit(self.pscan, port, target): port for port in range(start_p, end_p + 1)}
            
            for future in concurrent.futures.as_completed(futures):
                # Break the loop early if Cancel button was pressed
                if not self.is_scanning:
                    self.log("\n[-] Scan aborted by user.")
                    break
                
                port = futures[future]
                try:
                    is_open = future.result()
                    if is_open:
                        open_ports_count += 1
                        # Attempt to guess the service name for visual completeness
                        try:
                            service_name = socket.getservbyport(port, "tcp")
                        except OSError:
                            service_name = "unknown"
                            
                        self.log(f"{str(port)+'/tcp':<10} {'OPEN':<10} {service_name}")
                except Exception as e:
                    pass # Ignore connection errors

        # Reset UI state after scan finishes (or cancels)
        duration = round(time.time() - start_time, 2)
        if self.is_scanning:
            self.log("-" * 55)
            self.log(f"[+] Scan complete in {duration}s. Found {open_ports_count} open ports.")
        
        self.is_scanning = False
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.status_var.set("Status: Ready | Threads: 50 | Timeout: 0.5s")


if __name__ == '__main__':
    app = PortScannerApp()
    app.mainloop()