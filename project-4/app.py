import customtkinter as ctk
from tkinter import filedialog, messagebox
import main
import os

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")

class StegoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("StegoLSB - Image Message Hider & Extractor")
        self.geometry("820x520")
        self.resizable(False, False)

        # State variables for file paths
        self.encode_img_path = None
        self.decode_img_path = None

        self.setup_ui()

    def setup_ui(self):
        # --- ENCODE SECTION (Left) ---
        self.frame_encode = ctk.CTkFrame(self, width=390, height=480)
        self.frame_encode.place(x=10, y=20)

        ctk.CTkLabel(self.frame_encode, text="Hide Message", font=("Arial", 18, "bold")).place(x=15, y=10)

        # FIX: width moved to constructor
        self.btn_browse_enc = ctk.CTkButton(self.frame_encode, text="1. Select Carrier Image (PNG/JPG)", width=360, command=self.browse_encode_img)
        self.btn_browse_enc.place(x=15, y=55)
        
        self.lbl_enc_path = ctk.CTkLabel(self.frame_encode, text="No image selected", text_color="gray", width=360, anchor="w")
        self.lbl_enc_path.place(x=15, y=90)

        ctk.CTkLabel(self.frame_encode, text="2. Enter Secret Message:").place(x=15, y=125)
        self.txt_message = ctk.CTkTextbox(self.frame_encode, width=360, height=120)
        self.txt_message.place(x=15, y=155)

        ctk.CTkLabel(self.frame_encode, text="Password (Required):").place(x=15, y=290)
        self.ent_enc_pwd = ctk.CTkEntry(self.frame_encode, width=360, show="*")
        self.ent_enc_pwd.place(x=15, y=320)

        # FIX: width and height moved to constructor
        self.btn_encode = ctk.CTkButton(self.frame_encode, text="3. Hide Message in Image", fg_color="#27ae60", hover_color="#2ecc71", width=360, height=40, command=self.run_encode)
        self.btn_encode.place(x=15, y=380)

        # --- DECODE SECTION (Right) ---
        self.frame_decode = ctk.CTkFrame(self, width=390, height=480)
        self.frame_decode.place(x=420, y=20)

        ctk.CTkLabel(self.frame_decode, text="Extract Message", font=("Arial", 18, "bold")).place(x=15, y=10)

        # FIX: width moved to constructor
        self.btn_browse_dec = ctk.CTkButton(self.frame_decode, text="1. Select Stego Image (PNG)", width=360, command=self.browse_decode_img)
        self.btn_browse_dec.place(x=15, y=55)

        self.lbl_dec_path = ctk.CTkLabel(self.frame_decode, text="No image selected", text_color="gray", width=360, anchor="w")
        self.lbl_dec_path.place(x=15, y=90)

        ctk.CTkLabel(self.frame_decode, text="2. Enter Password:").place(x=15, y=125)
        self.ent_dec_pwd = ctk.CTkEntry(self.frame_decode, width=360, show="*")
        self.ent_dec_pwd.place(x=15, y=155)

        # FIX: width and height moved to constructor
        self.btn_decode = ctk.CTkButton(self.frame_decode, text="3. Extract Hidden Message", fg_color="#d35400", hover_color="#e67e22", width=360, height=40, command=self.run_decode)
        self.btn_decode.place(x=15, y=210)

        ctk.CTkLabel(self.frame_decode, text="Extracted Output:").place(x=15, y=275)
        self.txt_output = ctk.CTkTextbox(self.frame_decode, width=360, height=145, state="disabled", fg_color="#1e1e1e")
        self.txt_output.place(x=15, y=305)

    def browse_encode_img(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if filepath:
            self.encode_img_path = filepath
            # Format path for display so it doesn't break the UI layout
            display_path = filepath if len(filepath) < 45 else "..." + filepath[-42:]
            self.lbl_enc_path.configure(text=display_path)

    def browse_decode_img(self):
        # Stego images from our script are saved as PNG to prevent compression data loss
        filepath = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
        if filepath:
            self.decode_img_path = filepath
            display_path = filepath if len(filepath) < 45 else "..." + filepath[-42:]
            self.lbl_dec_path.configure(text=display_path)

    def run_encode(self):
        if not self.encode_img_path:
            messagebox.showwarning("Missing Input", "Please select a carrier image first.")
            return
        
        text = self.txt_message.get("1.0", "end-1c").strip()
        pwd = self.ent_enc_pwd.get().strip()

        if not text:
            messagebox.showwarning("Missing Input", "The secret message cannot be empty.")
            return
        if not pwd:
            messagebox.showwarning("Missing Input", "A password is required to secure the message.")
            return

        try:
            main.encode(self.encode_img_path, text, pwd)
            
            # Figure out where the file was saved based on main.py logic
            filename, _ = os.path.splitext(self.encode_img_path)
            outimg = filename + "_en.png"
            
            messagebox.showinfo("Success", f"Message successfully embedded!\n\nSaved to:\n{outimg}")
            
            # Clear UI on success
            self.txt_message.delete("1.0", "end")
            self.ent_enc_pwd.delete(0, "end")
            
        except ValueError as e:
            # Catches the specific max_capacity error you wrote in main.py
            messagebox.showerror("Capacity Limit", str(e))
        except Exception as e:
            messagebox.showerror("Encoding Error", f"Failed to encode image:\n\n{str(e)}")

    def run_decode(self):
        if not self.decode_img_path:
            messagebox.showwarning("Missing Input", "Please select an encoded stego image first.")
            return
        
        pwd = self.ent_dec_pwd.get().strip()
        if not pwd:
            messagebox.showwarning("Missing Input", "Please enter the decryption password.")
            return

        # Prepare text box for new output
        self.txt_output.configure(state="normal")
        self.txt_output.delete("1.0", "end")

        try:
            result = main.decode(self.decode_img_path, pwd)
            
            # Check for the specific error strings returned by main.py
            if result in ["No hidden message found.", "Incorrect password"]:
                messagebox.showerror("Extraction Failed", result)
                self.txt_output.insert("1.0", "[Failed to extract message]")
            else:
                self.txt_output.insert("1.0", result)
                
        except Exception as e:
            messagebox.showerror("Decoding Error", f"A fatal error occurred during decoding:\n\n{str(e)}")
            self.txt_output.insert("1.0", "[Error during extraction]")
            
        finally:
            self.txt_output.configure(state="disabled")

if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()