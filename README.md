# Cross-Platform Build Tools Boilerplate

This boilerplate provides a robust build system for Python applications, supporting Windows, Linux, and macOS platforms.

## Features

- Cross-platform build support (Windows, Linux, macOS)
- Platform-specific configurations
- Automatic code signing for macOS
- Windows executable metadata
- Linux desktop integration
- Clean build support
- Logging system

## Files

- `build.py`: Cross-platform build script with PyInstaller integration
- `build_config.json`: Platform-specific build configurations
- `entitlements.plist`: macOS entitlements (for macOS builds)

## Usage

1. Copy this boilerplate to your project:
```bash
cp -r boilerplate/* your-project/
```

2. Configure your build settings in `build_config.json`:
```json
{
    "base": {
        "app_name": "YourApp",
        "version": "1.0.0",
        "main_script": "main.py"
    },
    "windows": {
        "icon_file": "icons/app_icon.ico",
        "console": false
    },
    "macos": {
        "icon_file": "icons/app_icon.icns",
        "bundle_identifier": "com.example.yourapp"
    },
    "linux": {
        "icon_file": "icons/app_icon.png",
        "categories": "Utility;"
    }
}
```

3. Prepare your icons:
   - Windows: `icons/app_icon.ico`
   - macOS: `icons/app_icon.icns`
   - Linux: `icons/app_icon.png`

4. Run the build script:
```bash
# Clean build
python build.py --clean

# Build with custom config
python build.py --config custom_config.json
```

## Platform-Specific Features

### Windows
- Executable metadata (version info)
- UAC elevation support
- Icon integration
- Console/GUI mode selection

### macOS
- Code signing with certificate detection
- Entitlements management
- Bundle identifier
- Info.plist customization

### Linux
- Desktop file generation
- Icon integration
- Category specification
- Console/GUI mode selection

## Build Configuration

The `build_config.json` file uses a platform-specific structure:

### Base Configuration
- `app_name`: Application name
- `version`: Application version
- `main_script`: Entry point script
- `build_dir`: Build directory
- `dist_dir`: Distribution directory
- `additional_data`: Additional files to include
- `hidden_imports`: Python imports to include
- `exclude_modules`: Modules to exclude

### Windows-Specific
- `console`: Show console window
- `admin_access`: Require admin privileges
- `uac_admin`: UAC elevation
- `version_file`: Version info file

### macOS-Specific
- `bundle_identifier`: Bundle identifier
- `entitlements_file`: Entitlements file
- `info_plist`: Info.plist template

### Linux-Specific
- `desktop_file`: Desktop entry file
- `categories`: Application categories
- `console`: Show console window

## Code Signing

### Windows
- Sign executables using Windows SDK tools (future feature)

### macOS
Automatic certificate detection in order of preference:
1. Developer ID Application
2. Apple Development
3. 3rd Party Mac Developer Application
4. Mac Developer

### Linux
- No signing required by default
- Optional GPG signing available

## Requirements

### All Platforms
- Python 3.7+
- PyInstaller

### Windows
- Windows SDK (optional, for signing)
- .NET Framework

### macOS
- Xcode Command Line Tools
- Developer certificate (for signing)

### Linux
- GTK libraries (for GUI applications)
- Desktop integration tools

## Best Practices

1. Use version control
2. Keep platform-specific assets separate
3. Test on all target platforms
4. Use virtual environments
5. Keep dependencies updated

## Troubleshooting

### Windows Issues
- Check PATH environment
- Verify SDK installation
- Test UAC settings

### macOS Issues
- Verify certificate validity
- Check entitlements
- Test sandbox compliance

### Linux Issues
- Verify library dependencies
- Check desktop integration
- Test file permissions

## License

[Your License Here]
