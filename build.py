#!/usr/bin/env python3
"""
Cross-platform build script for Python applications.
Supports Windows, Linux, and macOS with platform-specific configurations.
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
import argparse
import json
import re
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlatformConfig:
    """Platform-specific configurations and utilities."""
    
    @staticmethod
    def get_platform():
        """Get current platform identifier."""
        if sys.platform == 'win32':
            return 'windows'
        elif sys.platform == 'darwin':
            return 'macos'
        else:
            return 'linux'
    
    @staticmethod
    def get_executable_extension():
        """Get platform-specific executable extension."""
        return '.exe' if sys.platform == 'win32' else ''
    
    @staticmethod
    def get_icon_extension():
        """Get platform-specific icon extension."""
        if sys.platform == 'win32':
            return '.ico'
        elif sys.platform == 'darwin':
            return '.icns'
        else:
            return '.png'

class BuildConfig:
    """Handles build configuration and settings."""
    
    def __init__(self, config_file='build_config.json'):
        self.config_file = config_file
        self.platform = PlatformConfig.get_platform()
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge platform-specific config with base config
                platform_config = config.get(self.platform, {})
                base_config = config.get('base', {})
                return {**base_config, **platform_config}
        return self._default_config()
    
    def _default_config(self):
        """Return default configuration."""
        base_config = {
            "app_name": "YourApp",
            "version": "1.0.0",
            "main_script": "main.py",
            "build_dir": "build",
            "dist_dir": "dist",
            "additional_data": [],
            "hidden_imports": [],
            "exclude_modules": [],
            "icon_file": f"icons/app_icon{PlatformConfig.get_icon_extension()}"
        }
        
        # Platform-specific defaults
        platform_configs = {
            "windows": {
                "console": False,
                "admin_access": False,
                "uac_admin": False,
                "version_file": "version.txt"
            },
            "macos": {
                "bundle_identifier": "com.example.yourapp",
                "entitlements_file": "entitlements.plist",
                "info_plist": "Info.plist"
            },
            "linux": {
                "console": False,
                "desktop_file": "app.desktop",
                "categories": "Utility;"
            }
        }
        
        return {**base_config, **platform_configs.get(self.platform, {})}
    
    def save(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

class WindowsBuilder:
    """Windows-specific build operations."""
    
    @staticmethod
    def create_version_info(config):
        """Create version info file for Windows."""
        # Parse version string into tuple
        version_parts = config['version'].split('.')
        while len(version_parts) < 4:
            version_parts.append('0')
        version_tuple = ','.join(version_parts)
        
        # Get company info
        company = config.get('company', {})
        company_name = company.get('name', 'Unknown Company')
        copyright_info = company.get('copyright', f'Copyright (c) {company_name}')
        description = company.get('description', config['app_name'])
        product_name = company.get('product_name', config['app_name'])
        trademark = company.get('trademark', company_name)
        
        version_info = f'''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{company_name}'),
         StringStruct(u'FileDescription', u'{description}'),
         StringStruct(u'FileVersion', u'{config["version"]}'),
         StringStruct(u'InternalName', u'{config["app_name"]}'),
         StringStruct(u'LegalCopyright', u'{copyright_info}'),
         StringStruct(u'LegalTrademarks', u'{trademark}'),
         StringStruct(u'OriginalFilename', u'{config["app_name"]}.exe'),
         StringStruct(u'ProductName', u'{product_name}'),
         StringStruct(u'ProductVersion', u'{config["version"]}')]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        with open('version_info.txt', 'w') as f:
            f.write(version_info)
        return 'version_info.txt'

class LinuxBuilder:
    """Linux-specific build operations."""
    
    @staticmethod
    def create_desktop_file(config):
        """Create .desktop file for Linux."""
        desktop_content = f"""[Desktop Entry]
Name={config['app_name']}
Exec={config['app_name']}
Icon={config['app_name']}
Type=Application
Categories={config.get('categories', 'Utility;')}
Version={config['version']}
"""
        desktop_file = os.path.join(config['build_dir'], f"{config['app_name']}.desktop")
        os.makedirs(os.path.dirname(desktop_file), exist_ok=True)
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        return desktop_file

class MacOSBuilder:
    """macOS-specific build operations."""
    
    @staticmethod
    def get_signing_identity():
        """Get the best available signing identity."""
        try:
            result = subprocess.run(
                ['security', 'find-identity', '-v', '-p', 'codesigning'],
                capture_output=True, text=True, check=True
            )
            
            identities = {
                'Developer ID Application': None,
                'Apple Development': None,
                '3rd Party Mac Developer Application': None,
                'Mac Developer': None
            }
            
            for line in result.stdout.splitlines():
                for identity in identities.keys():
                    if identity in line:
                        match = re.search(r'([A-F0-9]{40})', line)
                        if match:
                            identities[identity] = match.group(1)
                            break
            
            for identity, hash_value in identities.items():
                if hash_value:
                    logger.info(f"Using signing identity: {identity}")
                    return hash_value
            
            logger.warning("No preferred signing identity found. Using ad-hoc signing.")
            return '-'
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking signing identities: {e}")
            return '-'
    
    @staticmethod
    def sign_app(app_path, config):
        """Sign the macOS application bundle."""
        try:
            signing_identity = MacOSBuilder.get_signing_identity()
            
            cmd = [
                'codesign',
                '--force',
                '--deep',
                '--timestamp',
                '--options', 'runtime',
                '--entitlements', config['entitlements_file'],
                '-s', signing_identity,
                app_path
            ]
            
            subprocess.run(cmd, check=True)
            logger.info("Application signed successfully!")
            
            # Verify the signature
            subprocess.run(['codesign', '--verify', '--deep', '--strict', app_path], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during code signing: {e}")
            return False

class AppBuilder:
    """Cross-platform application builder."""
    
    def __init__(self, config):
        self.config = config
        self.platform = PlatformConfig.get_platform()
        self.platform_builders = {
            'windows': WindowsBuilder,
            'linux': LinuxBuilder,
            'macos': MacOSBuilder
        }
    
    def clean(self):
        """Clean build and dist directories."""
        for directory in [self.config.config['build_dir'], self.config.config['dist_dir']]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                logger.info(f"Cleaned {directory} directory")
    
    def prepare_platform_specific(self):
        """Prepare platform-specific build requirements."""
        builder = self.platform_builders.get(self.platform)
        if not builder:
            return []
            
        extra_args = []
        
        if self.platform == 'windows':
            version_file = builder.create_version_info(self.config.config)
            extra_args.extend(['--version-file', version_file])
            if self.config.config.get('uac_admin'):
                extra_args.append('--uac-admin')
            
        elif self.platform == 'linux':
            builder.create_desktop_file(self.config.config)
            
        return extra_args
    
    def build(self):
        """Build the application."""
        try:
            # Prepare PyInstaller command
            cmd = [
                'pyinstaller',
                '--name', self.config.config['app_name'],
                '--noconfirm',
                '--clean'
            ]
            
            # Add platform-specific options
            if self.platform == 'windows' or self.platform == 'macos':
                if not self.config.config.get('console', False):
                    cmd.append('--windowed')
            
            # Add icon if specified
            if 'icon_file' in self.config.config:
                cmd.extend(['--icon', self.config.config['icon_file']])
            
            # Add platform-specific arguments
            cmd.extend(self.prepare_platform_specific())
            
            # Add macOS bundle identifier
            if self.platform == 'macos' and 'bundle_identifier' in self.config.config:
                cmd.extend(['--osx-bundle-identifier', self.config.config['bundle_identifier']])
            
            # Add hidden imports
            for imp in self.config.config['hidden_imports']:
                cmd.extend(['--hidden-import', imp])
            
            # Add data files
            for src, dst in self.config.config['additional_data']:
                cmd.extend(['--add-data', f'{src}{os.pathsep}{dst}'])
            
            # Add main script
            cmd.append(self.config.config['main_script'])
            
            # Run PyInstaller
            subprocess.run(cmd, check=True)
            logger.info("Application built successfully!")
            
            # Handle platform-specific post-build steps
            if self.platform == 'macos':
                app_path = os.path.join(
                    self.config.config['dist_dir'],
                    f"{self.config.config['app_name']}.app"
                )
                MacOSBuilder.sign_app(app_path, self.config.config)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error building application: {e}")
            return False

def main():
    """Main build script entry point."""
    parser = argparse.ArgumentParser(description='Build cross-platform application')
    parser.add_argument('--clean', action='store_true', help='Clean build directories')
    parser.add_argument('--config', default='build_config.json', help='Build configuration file')
    args = parser.parse_args()
    
    # Load configuration
    config = BuildConfig(args.config)
    builder = AppBuilder(config)
    
    # Clean if requested
    if args.clean:
        builder.clean()
    
    # Build the application
    if builder.build():
        logger.info("Build completed successfully!")
    else:
        logger.error("Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
