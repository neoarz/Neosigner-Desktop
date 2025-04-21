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

# Install tkinter
echo "🖥️ Installing tkinter..."
brew install python-tk
brew install python-tk@3.13


# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install dependencies via brew
echo "🔄 Updating Homebrew..."
brew update

echo "📦 Installing dependencies..."
brew install pkg-config openssl minizip ideviceinstaller

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
echo "🎉 Setup complete! You can now run iPASideloader with: python3 zsign_gui.py"
echo "   Make sure to restart your terminal or run 'source ~/.zshrc' (or equivalent) to update your PATH." 