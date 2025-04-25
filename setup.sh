#!/bin/bash

# iPASideloader setup script
# Installs all required dependencies for iPASideloader

echo "📱 iPASideloader Setup"
echo "======================="
echo "This script will install the necessary dependencies for iPASideloader"
echo

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "❌ Error: This script is only compatible with macOS"
  exit 1
fi

# Check if brew is installed
if ! command -v brew &>/dev/null; then
  echo "🍺 Homebrew is not installed. Installing now..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  
  if ! command -v brew &>/dev/null; then
    echo "❌ Failed to install Homebrew. Please install it manually from https://brew.sh"
    exit 1
  fi
else
  echo "✅ Homebrew already installed"
fi

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
  echo "🐍 Python 3 is not installed. Installing now..."
  brew install python
  
  if ! command -v python3 &>/dev/null; then
    echo "❌ Failed to install Python 3. Please install it manually."
    exit 1
  fi
else
  echo "✅ Python 3 already installed"
fi

# Check if pip3 is installed
if ! command -v pip3 &>/dev/null; then
  echo "📦 pip3 is not installed. Installing now..."
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  python3 get-pip.py
  rm get-pip.py
  
  if ! command -v pip3 &>/dev/null; then
    echo "❌ Failed to install pip3. Please install it manually."
    exit 1
  fi
else
  echo "✅ pip3 already installed"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f requirements.txt ]; then
  pip3 install -r requirements.txt
else
  # Install minimal required packages if no requirements.txt
  pip3 install pyinstaller pillow
fi

# Install dependencies via brew
echo "🔄 Updating Homebrew..."
brew update

echo "📦 Installing basic dependencies..."
brew install pkg-config openssl minizip

# Install libimobiledevice and ideviceinstaller
echo "📱 Installing libimobiledevice and ideviceinstaller..."

# Try installing from Homebrew first
if brew list --formula | grep -q "^libimobiledevice$"; then
  echo "✅ libimobiledevice already installed"
else
  echo "Installing libimobiledevice..."
  brew install libimobiledevice
fi

# Check if ideviceinstaller is already installed
if command -v ideviceinstaller &>/dev/null; then
  echo "✅ ideviceinstaller already installed"
else
  echo "Installing ideviceinstaller..."
  # First try the Homebrew formula if it exists
  if brew list --formula | grep -q "^ideviceinstaller$"; then
    echo "Using Homebrew formula for ideviceinstaller"
    brew install ideviceinstaller
  else
    # If the formula doesn't exist, try installing from source
    echo "Homebrew formula for ideviceinstaller not found, installing from source..."
    
    # Install libimobiledevice dependencies
    brew install libtool autoconf automake libplist libzip

    # Clone and install ideviceinstaller
    git clone https://github.com/libimobiledevice/ideviceinstaller.git
    cd ideviceinstaller
    ./autogen.sh
    make
    make install
    cd ..
    rm -rf ideviceinstaller
  fi
fi

# Install create-dmg
if command -v create-dmg &>/dev/null; then
  echo "✅ create-dmg already installed"
else
  echo "Installing create-dmg..."
  brew install create-dmg
fi

# Check if the zsign directory already exists
if [ -d "zsign" ]; then
  echo "📁 zsign directory already exists. Updating..."
  cd zsign
  git pull
  cd ..
else
  echo "🔍 Cloning zsign repository..."
  git clone https://github.com/zhlynn/zsign.git
fi

# Compile zsign
echo "🔨 Compiling zsign..."
cd zsign/build/macos
make clean && make
cd ../../..

# Copy zsign to the bin directory
echo "📋 Installing zsign..."
mkdir -p bin
cp zsign/build/macos/zsign bin/
echo "✅ zsign installed to ./bin/zsign"

# Create resources structure
mkdir -p resources/bin
cp bin/zsign resources/bin/
chmod +x resources/bin/zsign

# Copy ideviceinstaller and dependencies to resources
IDEVICEINSTALLER_PATH=$(which ideviceinstaller)
if [ -n "$IDEVICEINSTALLER_PATH" ]; then
  cp "$IDEVICEINSTALLER_PATH" resources/bin/
  chmod +x resources/bin/ideviceinstaller
fi

# Copy libimobiledevice utilities
for util in idevice_id ideviceinfo idevicename; do
  UTIL_PATH=$(which $util)
  if [ -n "$UTIL_PATH" ]; then
    cp "$UTIL_PATH" resources/bin/
    chmod +x resources/bin/$util
  fi
done

# Create app launcher script
echo "📝 Creating app launcher script..."
cat > app_launcher.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

# Get the application path
if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    application_path = os.path.dirname(sys.executable)
    # For Mac app bundles, resources should be in various possible locations
    # List all possible bin paths in order of preference
    possible_bin_paths = [
        os.path.join(application_path, 'bin'),                              # /Contents/MacOS/bin
        os.path.join(os.path.dirname(application_path), 'Resources', 'bin') # /Contents/Resources/bin
    ]
    
    # Find the first valid bin path
    bin_path = None
    for path in possible_bin_paths:
        if os.path.exists(path) and os.path.isdir(path):
            bin_path = path
            break
else:
    # Running as a script
    application_path = os.path.dirname(os.path.abspath(__file__))
    bin_path = os.path.join(application_path, 'resources', 'bin')

print(f"Application path: {application_path}")
print(f"Selected bin path: {bin_path}")

# Add bin directory to PATH
if bin_path and os.path.exists(bin_path):
    os.environ['PATH'] = f"{bin_path}:{os.environ.get('PATH', '')}"
    print(f"Added {bin_path} to PATH")
    
    # Debug: List bin directory contents
    print("Bin directory contents:")
    try:
        for f in os.listdir(bin_path):
            file_path = os.path.join(bin_path, f)
            is_exec = os.access(file_path, os.X_OK)
            print(f"  {f} - Executable: {is_exec}")
        
        # Make sure binaries are executable
        for binary in os.listdir(bin_path):
            binary_path = os.path.join(bin_path, binary)
            if os.path.isfile(binary_path) and not os.access(binary_path, os.X_OK):
                os.chmod(binary_path, 0o755)
                print(f"Made {binary_path} executable")
    except Exception as e:
        print(f"Error while accessing bin directory: {e}")
else:
    print(f"Warning: No valid bin path found!")
    for path in possible_bin_paths:
        print(f"  Checked: {path} - Exists: {os.path.exists(path)}")

# Import zsign_gui here to ensure PATH is set first
try:
    import zsign_gui
except ImportError as e:
    print(f"Error importing zsign_gui: {e}")
    tk.Tk().withdraw()
    messagebox.showerror("Error", f"Failed to import zsign_gui: {e}")
    sys.exit(1)

# Check if zsign is available
try:
    zsign_path = None
    if bin_path:
        zsign_path = os.path.join(bin_path, "zsign")
        if os.path.exists(zsign_path):
            print(f"Found zsign at: {zsign_path}")
        else:
            print(f"zsign not found at expected path: {zsign_path}")
    
    # Try to run zsign to verify it works
    result = subprocess.run(["zsign", "-v"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          text=True,
                          env=os.environ)
    print(f"zsign version check result: {result.returncode}")
    print(f"zsign output: {result.stdout}")
    if result.stderr:
        print(f"zsign stderr: {result.stderr}")
except Exception as e:
    print(f"Error checking zsign: {e}")

# Launch the GUI
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = zsign_gui.ZsignGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error launching app: {e}")
        if 'root' in locals() and root.winfo_exists():
            messagebox.showerror("Error", f"Failed to launch app: {e}")
        else:
            tk_root = tk.Tk()
            tk_root.withdraw()
            messagebox.showerror("Error", f"Failed to launch app: {e}")
        sys.exit(1)
EOF
chmod +x app_launcher.py

# Create app icon
echo "🎨 Creating app icon..."
mkdir -p app_icon.iconset
if [ -f "assets/Icon.png" ]; then
  echo "Using existing icon from assets/Icon.png"
  python3 - << 'EOF'
from PIL import Image
import os

# Create iconset directory if it doesn't exist
os.makedirs("app_icon.iconset", exist_ok=True)

# Icon sizes needed for macOS
sizes = [16, 32, 64, 128, 256, 512, 1024]

try:
    # Load the source image
    source_img = Image.open("assets/Icon.png")
    
    # Process image for each size
    for size in sizes:
        # Resize the image while maintaining aspect ratio
        img = source_img.copy()
        img = img.resize((size, size), Image.LANCZOS)
        
        # Save icon in various sizes
        img.save(f"app_icon.iconset/icon_{size}x{size}.png")
        
        # Save @2x versions where applicable
        if size * 2 <= 1024:
            img_2x = source_img.copy()
            img_2x = img_2x.resize((size * 2, size * 2), Image.LANCZOS)
            img_2x.save(f"app_icon.iconset/icon_{size}x{size}@2x.png")
    
    print("App icons generated successfully!")
except Exception as e:
    print(f"Error processing app icon: {e}")
    # Create a simple fallback icon if we couldn't process the image
    for size in sizes:
        img = Image.new('RGBA', (size, size), color=(52, 152, 219))
        img.save(f"app_icon.iconset/icon_{size}x{size}.png")
        
        if size * 2 <= 1024:
            img_2x = Image.new('RGBA', (size * 2, size * 2), color=(52, 152, 219))
            img_2x.save(f"app_icon.iconset/icon_{size}x{size}@2x.png")
    
    print("Created fallback icons due to error with source image")
EOF
else
  echo "No icon found in assets/Icon.png, creating default icon"
  mkdir -p assets
  python3 - << 'EOF'
from PIL import Image, ImageDraw
import os

# Create assets directory if it doesn't exist
os.makedirs("assets", exist_ok=True)

# Create a default icon
size = 1024
img = Image.new('RGBA', (size, size), color=(52, 152, 219, 255))
draw = ImageDraw.Draw(img)

# Add simple stylized 'N' to the icon
draw.polygon([(size/4, size/4), (size/4, size*3/4), (size*3/4, size/4), (size*3/4, size*3/4)], 
             fill=(255, 255, 255, 230), outline=(255, 255, 255, 255))

# Save the icon
img.save("assets/Icon.png")

# Create iconset for different sizes
os.makedirs("app_icon.iconset", exist_ok=True)
sizes = [16, 32, 64, 128, 256, 512, 1024]

for size in sizes:
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(f"app_icon.iconset/icon_{size}x{size}.png")
    
    if size * 2 <= 1024:
        resized_2x = img.resize((size * 2, size * 2), Image.LANCZOS)
        resized_2x.save(f"app_icon.iconset/icon_{size}x{size}@2x.png")

print("Created default icon and iconset")
EOF
fi

# Convert iconset to icns
iconutil -c icns app_icon.iconset
echo "✅ Created app_icon.icns"

# Create PyInstaller spec file
echo "📄 Creating PyInstaller spec file..."
cat > NeoSigner.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/bin', 'bin'),
        ('zsign_gui.py', '.'),
        ('assets/Icon.png', 'assets'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.scrolledtext'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NeoSigner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False to hide terminal window
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.icns',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NeoSigner',
)
app = BUNDLE(
    coll,
    name='NeoSigner.app',
    bundle_identifier='com.neoarz.neosigner',
    icon='app_icon.icns',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleName': 'NeoSigner',
        'CFBundleDisplayName': 'NeoSigner',
        'CFBundleExecutable': 'NeoSigner',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.developer-tools',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'LSMinimumSystemVersion': '10.14.0'
    },
)
EOF

echo
echo "🚀 Do you want to build the NeoSigner app now? (y/n)"
read -r build_now

if [[ "$build_now" == "y" || "$build_now" == "Y" ]]; then
  # Check if PyInstaller is installed
  if ! python3 -c "import PyInstaller" &>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
  fi
  
  echo "🔨 Building NeoSigner.app..."
  pyinstaller --clean NeoSigner.spec
  
  if [ $? -eq 0 ]; then
    echo "✅ Successfully built NeoSigner.app"
    echo "📱 The app is located at: $(pwd)/dist/NeoSigner.app"
    
    echo "🔄 Would you like to create a DMG installer? (y/n)"
    read -r create_dmg
    
    if [[ "$create_dmg" == "y" || "$create_dmg" == "Y" ]]; then
      # Create DMG background
      echo "🎨 Creating DMG background..."
      python3 - << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import os

# Create a nice gradient background
width, height = 600, 400
background = Image.new('RGBA', (width, height), color=(240, 240, 240, 255))

# Add a subtle gradient
draw = ImageDraw.Draw(background)
for y in range(height):
    # Create a vertical gradient from light blue to white
    color = (52, 152, 219, int(255 * (1 - y / height)))
    draw.line([(0, y), (width, y)], fill=color)

# Add text
try:
    # Try to use a font, falling back as needed
    font_size = 32
    try:
        # Try system font first
        font = ImageFont.truetype("Arial Bold", font_size)
    except:
        # Fall back to default
        font = ImageFont.load_default()
        
    draw.text((width/2, height/2 - 50), "NeoSigner", font=font, fill=(40, 40, 40), anchor="mm")
    
    font_size = 16
    try:
        font_small = ImageFont.truetype("Arial", font_size)
    except:
        font_small = font
        
    draw.text((width/2, height/2 + 20), "Drag the application to the Applications folder", 
            font=font_small, fill=(80, 80, 80), anchor="mm")
except Exception as e:
    print(f"Error adding text to background: {e}")

# Save the background
background.save("dmg_background.png")
print("Created DMG background image")
EOF
      
      # Create DMG
      echo "📀 Creating DMG installer..."
      mkdir -p dmg_contents
      cp -R dist/NeoSigner.app dmg_contents/
      ln -s /Applications dmg_contents/Applications
      
      VERSION="1.0.0"
      create-dmg \
        --volname "NeoSigner" \
        --volicon "app_icon.icns" \
        --background "dmg_background.png" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "NeoSigner.app" 150 190 \
        --icon "Applications" 450 190 \
        --hide-extension "NeoSigner.app" \
        --app-drop-link 450 190 \
        "NeoSigner-$VERSION.dmg" \
        "dmg_contents/"
      
      if [ $? -eq 0 ]; then
        echo "✅ DMG installer created: $(pwd)/NeoSigner-$VERSION.dmg"
      else
        echo "❌ Failed to create DMG installer"
      fi
      
      # Clean up
      rm -rf dmg_contents
    fi
  else
    echo "❌ Failed to build NeoSigner.app"
  fi
else
  echo "✅ Setup complete. You can build the app later by running:"
  echo "   pyinstaller --clean NeoSigner.spec"
fi

# Add to PATH if not already there
if [[ ":$PATH:" != *":$(pwd)/bin:"* ]]; then
  echo "📝 Adding bin directory to PATH in your shell profile..."
  
  # Determine which shell profile to use
  SHELL_PROFILE=""
  if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_PROFILE="$HOME/.zshrc"
  elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_PROFILE="$HOME/.bash_profile"
    if [ ! -f "$SHELL_PROFILE" ]; then
      SHELL_PROFILE="$HOME/.bashrc"
    fi
  fi
  
  if [ -n "$SHELL_PROFILE" ]; then
    echo "export PATH=\"\$PATH:$(pwd)/bin\"" >> "$SHELL_PROFILE"
    echo "✅ Added to $SHELL_PROFILE. Please restart your terminal or run 'source $SHELL_PROFILE'"
  else
    echo "⚠️ Could not determine your shell profile. Please add the following line to your shell profile manually:"
    echo "export PATH=\"\$PATH:$(pwd)/bin\""
  fi
fi

echo
echo "🎉 Setup complete!"
if [[ "$build_now" == "y" || "$build_now" == "Y" ]]; then
  echo "   You can find NeoSigner.app in the dist directory."
else
  echo "   You can run iPASideloader with: python3 zsign_gui.py"
  echo "   or build the app with: pyinstaller --clean NeoSigner.spec"
fi
echo "   Make sure to restart your terminal or run 'source ~/.zshrc' (or equivalent) to update your PATH." 