# Neosigner-Desktop (DO NOT FOLLOW THIS README; IT IS OUTDATED, USE THE WORKFLOW BUILD)

A user-friendly GUI wrapper for zsign and ideviceinstaller, making iOS app sideloading simpler for everyone.

## Features

- Simple drag-and-drop interface for IPA files
- One-click signing with custom certificates
- Bundle ID and app name modification
- Dylib injection support
- Direct installation to connected iOS devices
- Ad-hoc signing support
- Support for macOS, coming soon for Windows/Linux

## Requirements

- macOS 10.15+ (Catalina or newer)
- Python 3.6 or newer
- Internet connection for initial setup

## Installation

### Option 1: Download Release

1. Download the latest release from the [Releases](https://github.com/neoarz/iPASideloader/releases) page
2. Extract the ZIP file
3. Run the setup script to install dependencies: `./setup.sh`
4. Launch the app: `python zsign_gui.py`

### Option 2: Clone from Source

```bash
# Clone the repository
git clone https://github.com/neoarz/iPASideloader.git
cd iPASideloader

# Install dependencies
./setup.sh

# Run the app
python3 zsign_gui.py
```

## Setting Up Dependencies

iPASideloader requires zsign and ideviceinstaller to function. The setup script will install these automatically, or you can install them manually:

### Installing zsign

```bash
brew install pkg-config openssl minizip
git clone https://github.com/zhlynn/zsign.git
cd zsign/build/macos
make clean && make
sudo cp zsign /usr/local/bin/
```

### Installing ideviceinstaller

```bash
brew install ideviceinstaller
```

## Usage

1. **Launch iPASideloader**
   - Run `python zsign_gui.py` in  terminal

2. **Sign an IPA**
   - Drag and drop  IPA file into the app
   - Select  signing certificate and provisioning profile
   - Adjust settings as needed (bundle ID, app name, etc.)
   - Click "Sign"

3. **Install to Device**
   - Connect your iOS device via USB
   - Trust the computer on your device if prompted
   - Click "Install" to deploy the signed app

4. **Advanced Options**
   - Inject dylibs by clicking "Add Dylib" and selecting your files
   - Enable ad-hoc signing for testing without a developer account
   - Customize zip compression level for smaller IPAs

## Troubleshooting

### App Won't Install

- Ensure your device is connected and trusted
- Check that your provisioning profile matches your certificate
- Verify your device is included in the provisioning profile

### Signing Fails

- Make sure your certificate and provisioning profile are valid
- Check that zsign is properly installed
- Try reinstalling dependencies through the setup script

### Device Not Detected

- Reconnect your device and trust the computer
- Install/reinstall libimobiledevice: `brew reinstall libimobiledevice`
- Restart your computer and iOS device

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Credits

- [zsign](https://github.com/zhlynn/zsign) - The core signing tool
- [libimobiledevice](https://github.com/libimobiledevice/libimobiledevice) - iOS communication library
- [ideviceinstaller](https://github.com/libimobiledevice/ideviceinstaller) - App installation tool

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

iPASideloader is meant for legitimate app development and testing purposes only. Always respect copyright and terms of service for all applications. The developers of iPASideloader are not responsible for any misuse of this software. 
