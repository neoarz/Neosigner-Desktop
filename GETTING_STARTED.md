# Quick Start Guide for iPASideloader

This guide will help you get up and running with iPASideloader quickly.

## Setup (First-time only)

1. **Install Dependencies**

    Run the setup script:
    ```bash
    ./setup.sh
    ```
    
    This will install all required dependencies:
    - Homebrew (if needed)
    - pkg-config, openssl, minizip
    - ideviceinstaller
    - zsign (compiled from source)

2. **Verify Installation**

    Test that everything is working:
    ```bash
    python zsign_gui.py
    ```

    The GUI should open and show the zsign version in the logs tab.

## Signing an IPA

1. **Launch the app**
    ```bash
    python zsign_gui.py
    ```

2. **Basic Signing**
   
    From the "Basic" tab:
    - Click "Browse" to select an IPA file
    - Select a certificate file (.p12)
    - Enter the certificate password
    - Select a provisioning profile
    - Choose where to save the signed IPA
    - Click "Sign App"

3. **Ad-hoc Signing** (no certificate needed)
   
    From the "Basic" tab:
    - Click "Browse" to select an IPA file
    - Check "Ad-hoc Signature"
    - Choose where to save the signed IPA
    - Click "Sign App"

## Installing to Device

1. **Connect your device**
   
    Connect your iOS device via USB and trust the computer.

2. **Install signed app**
   
    Click "Install to Device" after signing is complete.

## Advanced Features

### Modifying Bundle ID/Name
1. Go to the "Advanced" tab
2. Enter a new Bundle ID and/or App Name
3. Return to the "Basic" tab and sign the app

### Injecting a Dylib
1. Go to the "Advanced" tab
2. Click "Browse" next to "Inject Dylib" and select your .dylib file
3. Check "Inject Dylib as Weak" if needed
4. Return to the "Basic" tab and sign the app

### Force Signing Without Cache
1. Go to the "Advanced" tab
2. Check "Force Sign Without Cache"
3. Return to the "Basic" tab and sign the app

## Troubleshooting

### Common errors

1. **"zsign binary not found"**:
   - Run `./setup.sh` again
   - Make sure zsign was compiled correctly in `./bin/zsign`

2. **"Certificate file not found"**:
   - Make sure your .p12 file path is correct
   - Check that the file exists and has proper permissions

3. **"Provisioning profile not found"**:
   - Verify the provisioning profile path is correct
   - Ensure the file exists and has proper permissions

4. **"No iOS device found"**:
   - Reconnect your device
   - Trust the computer on your device
   - Install/reinstall libimobiledevice: `brew reinstall libimobiledevice` 