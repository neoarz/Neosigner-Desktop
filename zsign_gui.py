import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

class ZsignGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoSigner")
        self.root.geometry("800x600")
        
        # Get the path to the zsign executable
        self.zsign_path = self.find_zsign_binary()
        if not self.zsign_path:
            self.prompt_for_zsign_path()
            if not self.zsign_path:
                root.destroy()
                return
        
        # Check for ideviceinstaller
        self.ideviceinstaller_path = self.find_ideviceinstaller()
        
        # Create a notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.basic_frame = ttk.Frame(self.notebook)
        self.advanced_frame = ttk.Frame(self.notebook)
        self.output_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.basic_frame, text="Basic")
        self.notebook.add(self.advanced_frame, text="Advanced")
        self.notebook.add(self.output_frame, text="Logs")
        
        # Create the UI elements
        self.create_basic_tab()
        self.create_advanced_tab()
        self.create_output_tab()
        
        # Append zsign version to output
        try:
            self.get_zsign_version()
            if self.ideviceinstaller_path:
                self.append_output(f"ideviceinstaller found: {self.ideviceinstaller_path}")
        except Exception as e:
            self.append_output(f"Warning: Could not get zsign version: {str(e)}")
    
    def prompt_for_zsign_path(self):
        """Prompt the user to manually locate the zsign binary"""
        result = messagebox.askquestion("Zsign Binary Not Found", 
                      "Could not find zsign binary automatically. Would you like to locate it manually?")
        
        if result == 'yes':
            if sys.platform == "win32":
                filetypes = [("Executable files", "*.exe"), ("All files", "*.*")]
            else:
                filetypes = [("All files", "*.*")]
            
            path = filedialog.askopenfilename(
                title="Select zsign binary",
                filetypes=filetypes
            )
            
            if path:
                if os.path.exists(path):
                    if sys.platform != "win32" and not os.access(path, os.X_OK):
                        messagebox.showerror("Error", "Selected file is not executable.")
                        return
                    self.zsign_path = path
                    messagebox.showinfo("Success", f"Using zsign binary at: {path}")
                else:
                    messagebox.showerror("Error", "Selected file does not exist.")
        else:
            messagebox.showerror("Error", 
                "Zsign binary is required to run this application. Please compile it according to the README instructions.")
    
    def find_ideviceinstaller(self):
        """Find ideviceinstaller binary for easy installation to device"""
        if sys.platform == "darwin":
            # Check common paths on macOS
            paths = [
                "/usr/local/bin/ideviceinstaller",
                "/opt/homebrew/bin/ideviceinstaller"
            ]
            
            for path in paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    return path
            
            # Try to find in PATH
            try:
                result = subprocess.run(["which", "ideviceinstaller"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
                if result.returncode == 0:
                    path = result.stdout.strip()
                    if path and os.path.exists(path):
                        return path
            except:
                pass
        
        return None
    
    def get_zsign_version(self):
        """Get the zsign version and display it in the output tab"""
        try:
            result = subprocess.run([self.zsign_path, "-v"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            version = result.stdout.strip() or result.stderr.strip()
            self.append_output(f"Zsign binary found: {self.zsign_path}")
            self.append_output(f"Version: {version}")
        except Exception as e:
            self.append_output(f"Error checking zsign version: {str(e)}")
    
    def find_zsign_binary(self):
        # Base directory is the directory containing this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get home directory
        home_dir = os.path.expanduser("~")
        
        if sys.platform == "darwin":
            # macOS
            paths = [
                os.path.join(base_dir, "bin", "zsign"),                  # Local bin directory
                os.path.join(base_dir, "zsign_exe"),
                os.path.join(base_dir, "zsign/bin/zsign"),
                os.path.join(base_dir, "build", "macos", "zsign"),
                os.path.join(base_dir, "zsign"),
                "/usr/local/bin/zsign",
                "/opt/homebrew/bin/zsign",                               # Homebrew on Apple Silicon
                os.path.join(home_dir, "zsign/bin/zsign"),               # User's home directory
                os.path.join(home_dir, "bin/zsign"),
                os.path.join(home_dir, ".local/bin/zsign"),
                "/usr/local/zsign/bin/zsign",
                "/usr/local/bin/zsign",
                "/usr/local/zsign/bin/zsign",
                "/zsign/bin/zsign"
            ]
            
            # Try to run 'which zsign' to find it in PATH
            try:
                result = subprocess.run(["which", "zsign"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip()
                    if os.path.exists(path):
                        paths.insert(0, path)  # Add to beginning of list
            except:
                pass
                
        elif sys.platform.startswith("linux"):
            # Linux
            paths = [
                os.path.join(base_dir, "bin", "zsign"),
                os.path.join(base_dir, "build", "linux", "zsign"),
                os.path.join(base_dir, "zsign"),
                os.path.join(home_dir, "zsign/bin/zsign"),
                os.path.join(home_dir, "bin/zsign"),
                os.path.join(home_dir, ".local/bin/zsign"),
                "/usr/local/bin/zsign",
                "/usr/bin/zsign"
            ]
        elif sys.platform == "win32":
            # Windows
            paths = [
                os.path.join(base_dir, "bin", "zsign.exe"),
                os.path.join(base_dir, "build", "windows", "vs2022", "x64", "Release", "zsign.exe"),
                os.path.join(base_dir, "zsign.exe")
            ]
        else:
            # Unknown platform
            return None
        
        # Print search paths to output for debugging
        print(f"Searching for zsign binary in the following paths:")
        for path in paths:
            print(f"  - {path}")
            
        # Check if binary exists and is executable
        for path in paths:
            if os.path.exists(path):
                if sys.platform != "win32":
                    # On Unix-like systems, check if the file is executable
                    if os.access(path, os.X_OK):
                        print(f"Found zsign binary at: {path}")
                        return path
                else:
                    # On Windows, just check if it exists
                    print(f"Found zsign binary at: {path}")
                    return path
        
        return None
    
    def create_basic_tab(self):
        frame = self.basic_frame
        
        # Input file/folder
        ttk.Label(frame, text="Unsigned App (.ipa):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_entry = ttk.Entry(frame, width=50)
        self.input_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Private key or p12 file
        ttk.Label(frame, text="Certificate File (.p12):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.pkey_entry = ttk.Entry(frame, width=50)
        self.pkey_entry.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_pkey).grid(row=1, column=2, padx=5, pady=5)
        
        # Password
        ttk.Label(frame, text="Certificate Password:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.password_entry = ttk.Entry(frame, width=50, show="*")
        self.password_entry.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        
        # Provisioning profile
        ttk.Label(frame, text="Provisioning Profile:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.prov_entry = ttk.Entry(frame, width=50)
        self.prov_entry.grid(row=3, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_prov).grid(row=3, column=2, padx=5, pady=5)
        
        # Output file
        ttk.Label(frame, text="Signed App Location:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = ttk.Entry(frame, width=50)
        self.output_entry.grid(row=4, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_output).grid(row=4, column=2, padx=5, pady=5)
        
        # Ad-hoc checkbox
        self.adhoc_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Ad-hoc Signature (No certificate needed)", variable=self.adhoc_var).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Sign button
        ttk.Button(frame, text="Sign App", command=self.sign).grid(row=6, column=0, padx=5, pady=20)
        
        # Install button (only show if ideviceinstaller is available)
        if self.ideviceinstaller_path:
            ttk.Button(frame, text="Install to Device", command=self.install_to_device).grid(row=6, column=1, padx=5, pady=20)
        
        # Add some stretching
        frame.columnconfigure(1, weight=1)
    
    def create_advanced_tab(self):
        frame = self.advanced_frame
        
        # Certificate file
        ttk.Label(frame, text="Additional Certificate:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cert_entry = ttk.Entry(frame, width=50)
        self.cert_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_cert).grid(row=0, column=2, padx=5, pady=5)
        
        # Bundle ID
        ttk.Label(frame, text="Override Bundle ID:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.bundle_id_entry = ttk.Entry(frame, width=50)
        self.bundle_id_entry.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        
        # Bundle Name
        ttk.Label(frame, text="Override App Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.bundle_name_entry = ttk.Entry(frame, width=50)
        self.bundle_name_entry.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        
        # Bundle Version
        ttk.Label(frame, text="Override App Version:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.bundle_version_entry = ttk.Entry(frame, width=50)
        self.bundle_version_entry.grid(row=3, column=1, sticky="we", padx=5, pady=5)
        
        # Entitlements
        ttk.Label(frame, text="Entitlements File:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.entitlements_entry = ttk.Entry(frame, width=50)
        self.entitlements_entry.grid(row=4, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_entitlements).grid(row=4, column=2, padx=5, pady=5)
        
        # Dylib
        ttk.Label(frame, text="Inject Dylib:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.dylib_entry = ttk.Entry(frame, width=50)
        self.dylib_entry.grid(row=5, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_dylib).grid(row=5, column=2, padx=5, pady=5)
        
        # Weak checkbox
        self.weak_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Inject Dylib as Weak", variable=self.weak_var).grid(row=6, column=0, sticky="w", padx=5, pady=5)
        
        # Force checkbox
        self.force_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Force Sign Without Cache", variable=self.force_var).grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        # SHA256 only checkbox
        self.sha256_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="SHA256 Only", variable=self.sha256_var).grid(row=7, column=0, sticky="w", padx=5, pady=5)
        
        # Install checkbox
        self.install_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Install After Signing", variable=self.install_var).grid(row=7, column=1, sticky="w", padx=5, pady=5)
        
        # Zip level
        ttk.Label(frame, text="Zip Compression Level (0-9):").grid(row=8, column=0, sticky="w", padx=5, pady=5)
        self.zip_level_var = tk.StringVar(value="9")
        ttk.Spinbox(frame, from_=0, to=9, textvariable=self.zip_level_var, width=5).grid(row=8, column=1, sticky="w", padx=5, pady=5)
        
        # Add some stretching
        frame.columnconfigure(1, weight=1)
    
    def create_output_tab(self):
        frame = self.output_frame
        
        # Output text
        self.output_text = scrolledtext.ScrolledText(frame, width=80, height=30)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.output_text.config(state="disabled")
        
        # Clear button
        ttk.Button(frame, text="Clear Logs", command=self.clear_output).pack(pady=5)
    
    def browse_input(self):
        path = filedialog.askopenfilename(filetypes=[("IPA files", "*.ipa"), ("All files", "*.*")])
        if not path:
            path = filedialog.askdirectory()
        if path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)
    
    def browse_pkey(self):
        path = filedialog.askopenfilename(filetypes=[("Certificate files", "*.p12"), ("Key files", "*.pem"), ("All files", "*.*")])
        if path:
            self.pkey_entry.delete(0, tk.END)
            self.pkey_entry.insert(0, path)
    
    def browse_prov(self):
        path = filedialog.askopenfilename(filetypes=[("Provisioning Profile", "*.mobileprovision"), ("All files", "*.*")])
        if path:
            self.prov_entry.delete(0, tk.END)
            self.prov_entry.insert(0, path)
    
    def browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".ipa", filetypes=[("IPA files", "*.ipa"), ("All files", "*.*")])
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)
    
    def browse_cert(self):
        path = filedialog.askopenfilename(filetypes=[("Certificate files", "*.pem *.cer"), ("All files", "*.*")])
        if path:
            self.cert_entry.delete(0, tk.END)
            self.cert_entry.insert(0, path)
    
    def browse_entitlements(self):
        path = filedialog.askopenfilename(filetypes=[("Entitlements files", "*.plist *.xml"), ("All files", "*.*")])
        if path:
            self.entitlements_entry.delete(0, tk.END)
            self.entitlements_entry.insert(0, path)
    
    def browse_dylib(self):
        path = filedialog.askopenfilename(filetypes=[("Dylib files", "*.dylib"), ("All files", "*.*")])
        if path:
            self.dylib_entry.delete(0, tk.END)
            self.dylib_entry.insert(0, path)
    
    def clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")
    
    def append_output(self, text):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")
        self.root.update()
    
    def install_to_device(self):
        """Install the signed IPA to device using ideviceinstaller"""
        if not self.ideviceinstaller_path:
            messagebox.showerror("Error", "ideviceinstaller not found. Please install it first.")
            return
        
        output_file = self.output_entry.get().strip()
        if not output_file:
            messagebox.showerror("Error", "No signed app specified. Please sign an app first.")
            return
        
        if not os.path.exists(output_file):
            messagebox.showerror("Error", f"Signed app not found: {output_file}")
            return
        
        # Check if device is connected
        try:
            result = subprocess.run([self.ideviceinstaller_path, "-l"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            if "ERROR:" in result.stdout or "ERROR:" in result.stderr:
                messagebox.showerror("Error", "No iOS device found. Please connect your device.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error checking device: {str(e)}")
            return
        
        # Install the app
        self.append_output(f"Installing app to device: {output_file}")
        
        try:
            cmd = [self.ideviceinstaller_path, "-i", output_file]
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1
            )
            
            # Switch to output tab
            self.notebook.select(self.output_frame)
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.append_output(output.strip())
                self.root.update()
            
            return_code = process.poll()
            
            if return_code == 0:
                self.append_output("App installed successfully!")
                messagebox.showinfo("Success", "App installed successfully to your device!")
            else:
                self.append_output(f"Installation failed with code {return_code}")
                messagebox.showerror("Error", f"Installation failed with code {return_code}")
                
        except Exception as e:
            self.append_output(f"Installation error: {str(e)}")
            messagebox.showerror("Error", f"Installation error: {str(e)}")
    
    def sign(self):
        input_path = self.input_entry.get().strip()
        if not input_path:
            messagebox.showerror("Error", "Unsigned app (.ipa) is required.")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input path does not exist: {input_path}")
            return
        
        # Check if zsign binary exists
        if not os.path.exists(self.zsign_path):
            result = messagebox.askquestion("Error", 
                "Zsign binary not found. Would you like to specify the location manually?")
            if result == 'yes':
                self.prompt_for_zsign_path()
                if not self.zsign_path or not os.path.exists(self.zsign_path):
                    return
            else:
                return
        
        # Build the command
        cmd = [self.zsign_path]
        
        # Basic options
        if self.adhoc_var.get():
            cmd.append("-a")
        else:
            # When not adhoc, we need key and prov
            pkey = self.pkey_entry.get().strip()
            prov = self.prov_entry.get().strip()
            
            if not pkey:
                messagebox.showerror("Error", "Certificate file (.p12) is required unless using ad-hoc.")
                return
            if not prov:
                messagebox.showerror("Error", "Provisioning profile is required unless using ad-hoc.")
                return
            
            # Check if files exist
            if not os.path.exists(pkey):
                messagebox.showerror("Error", f"Certificate file not found: {pkey}")
                return
            if not os.path.exists(prov):
                messagebox.showerror("Error", f"Provisioning profile not found: {prov}")
                return
            
            cmd.extend(["-k", pkey])
            cmd.extend(["-m", prov])
            
            password = self.password_entry.get()
            if password:
                cmd.extend(["-p", password])
        
        # Output file
        output_file = self.output_entry.get().strip()
        if output_file:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create output directory: {str(e)}")
                    return
            cmd.extend(["-o", output_file])
        
        # Advanced options
        cert_file = self.cert_entry.get().strip()
        if cert_file:
            if not os.path.exists(cert_file):
                messagebox.showerror("Error", f"Certificate file not found: {cert_file}")
                return
            cmd.extend(["-c", cert_file])
        
        bundle_id = self.bundle_id_entry.get().strip()
        if bundle_id:
            cmd.extend(["-b", bundle_id])
        
        bundle_name = self.bundle_name_entry.get().strip()
        if bundle_name:
            cmd.extend(["-n", bundle_name])
        
        bundle_version = self.bundle_version_entry.get().strip()
        if bundle_version:
            cmd.extend(["-r", bundle_version])
        
        entitlements = self.entitlements_entry.get().strip()
        if entitlements:
            if not os.path.exists(entitlements):
                messagebox.showerror("Error", f"Entitlements file not found: {entitlements}")
                return
            cmd.extend(["-e", entitlements])
        
        dylib = self.dylib_entry.get().strip()
        if dylib:
            if not os.path.exists(dylib):
                messagebox.showerror("Error", f"Dylib file not found: {dylib}")
                return
            cmd.extend(["-l", dylib])
        
        if self.weak_var.get():
            cmd.append("-w")
        
        if self.force_var.get():
            cmd.append("-f")
        
        if self.sha256_var.get():
            cmd.append("-2")
        
        if self.install_var.get():
            cmd.append("-i")
        
        try:
            zip_level = int(self.zip_level_var.get())
            if 0 <= zip_level <= 9:
                cmd.extend(["-z", str(zip_level)])
        except ValueError:
            pass
        
        # Add the input path
        cmd.append(input_path)
        
        # Show command
        cmd_str = " ".join(cmd)
        self.append_output(f"Running command: {cmd_str}")
        
        # Run the command
        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Disable the sign button during signing
            self.notebook.tab(self.notebook.index(self.basic_frame), state="disabled")
            self.notebook.tab(self.notebook.index(self.advanced_frame), state="disabled")
            self.notebook.select(self.output_frame)
            self.root.update()
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.append_output(output.strip())
                self.root.update()
            
            # Check for any remaining output
            remaining_output = process.stdout.read()
            if remaining_output:
                self.append_output(remaining_output.strip())
            
            return_code = process.poll()
            
            # Re-enable tabs
            self.notebook.tab(self.notebook.index(self.basic_frame), state="normal")
            self.notebook.tab(self.notebook.index(self.advanced_frame), state="normal")
            
            if return_code == 0:
                self.append_output("\nSignature completed successfully!")
                
                # If output file exists, show its path
                if output_file and os.path.exists(output_file):
                    file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
                    self.append_output(f"Output file: {output_file} ({file_size:.2f} MB)")
                
                messagebox.showinfo("Success", "Signature completed successfully!")
                
                # Auto-install if ideviceinstaller is available and install after signing is checked
                if self.ideviceinstaller_path and self.install_var.get() and output_file and os.path.exists(output_file):
                    result = messagebox.askquestion("Install", 
                              "Would you like to install the signed app to your device now?")
                    if result == 'yes':
                        self.install_to_device()
            else:
                self.append_output(f"\nSignature failed with return code {return_code}")
                messagebox.showerror("Error", f"Signature failed with return code {return_code}")
                
        except Exception as e:
            self.append_output(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            
            # Re-enable tabs
            self.notebook.tab(self.notebook.index(self.basic_frame), state="normal")
            self.notebook.tab(self.notebook.index(self.advanced_frame), state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = ZsignGUI(root)
    root.mainloop() 
