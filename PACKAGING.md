# Building and Packaging Guide

This guide explains how to build and package the NLP Comment Processor as a standalone executable.

## Prerequisites

- Python 3.7 or higher
- All dependencies installed (`pip install -r requirements.txt`)

## Building the Executable

### Method 1: Using the Spec File (Recommended)

The project includes a PyInstaller specification file (`nlp_processor.spec`) that contains all the necessary configuration:

```bash
pyinstaller nlp_processor.spec
```

This will create:
- `build/` directory - Temporary build files (can be deleted)
- `dist/` directory - Contains the final executable

### Method 2: Direct PyInstaller Command

You can also build directly without the spec file:

```bash
pyinstaller --onefile --windowed --name NLPCommentProcessor gui.py
```

Options explained:
- `--onefile`: Package everything into a single executable
- `--windowed`: Don't show a console window (GUI mode)
- `--name`: Name of the output executable

### Platform-Specific Notes

#### Windows
- Executable will be: `dist/NLPCommentProcessor.exe`
- No console window will appear
- Users can double-click to run

#### Linux
- Executable will be: `dist/NLPCommentProcessor`
- Make it executable: `chmod +x dist/NLPCommentProcessor`
- Run with: `./dist/NLPCommentProcessor`

#### macOS
- Executable will be: `dist/NLPCommentProcessor`
- May need to allow in Security & Privacy settings
- Run with: `./dist/NLPCommentProcessor`

## Testing the Executable

1. Navigate to the `dist/` directory:
```bash
cd dist/
```

2. Run the executable:

**Windows:**
```bash
NLPCommentProcessor.exe
```

**Linux/macOS:**
```bash
./NLPCommentProcessor
```

3. Test with sample data:
   - Create sample data: `python ../create_sample_data.py`
   - Use the GUI to process the generated `sample_comments.json`

## Distribution

The executable in `dist/` is standalone and can be distributed to users who don't have Python installed.

### What's Included
- Python interpreter
- All required libraries (PyQt5, etc.)
- Your application code (gui.py, nlp.py)

### Distribution Checklist
- [ ] Test the executable on the target platform
- [ ] Include README with usage instructions
- [ ] Include sample JSON file for testing
- [ ] Verify no Python installation is required
- [ ] Check executable size (should be ~40-50 MB)

## Troubleshooting

### Build Errors

**Missing modules:**
```bash
pip install --upgrade pyinstaller PyQt5
```

**Import errors:**
Add missing modules to the spec file's `hiddenimports` list.

### Runtime Errors

**"Failed to execute script" error:**
- Test with `--debug` flag to see detailed errors
- Ensure all data files are included

**PyQt5 platform plugin errors:**
- Linux: Install `libxcb-xinerama0`
- May need to set `QT_QPA_PLATFORM=offscreen` for headless systems

### Size Optimization

The default executable includes all dependencies. To reduce size:

1. Use `--exclude-module` to remove unused libraries
2. Enable UPX compression (if available)
3. Use `--onedir` instead of `--onefile` for faster startup

## Advanced Configuration

### Adding an Icon

1. Create or obtain an `.ico` (Windows) or `.icns` (macOS) file
2. Modify the spec file:
```python
exe = EXE(
    ...
    icon='icon.ico',  # Add this line
)
```

### Including Data Files

If you need to include additional files:

```python
a = Analysis(
    ...
    datas=[('data_file.txt', '.')],  # (source, destination)
)
```

### Multiple Executables

To create separate executables for different platforms, run PyInstaller on each platform. Cross-compilation is not officially supported.

## Continuous Integration

For automated builds, add to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Build executable
  run: |
    pip install -r requirements.txt
    pyinstaller nlp_processor.spec
    
- name: Upload artifact
  uses: actions/upload-artifact@v2
  with:
    name: nlp-processor-${{ runner.os }}
    path: dist/
```

## File Structure After Build

```
nlp-project/
├── build/                    # Temporary build files (can delete)
├── dist/                     # Final executable
│   └── NLPCommentProcessor   # The standalone executable
├── gui.py                    # Source files
├── nlp.py
├── nlp_processor.spec       # PyInstaller config
└── requirements.txt
```

## Clean Build

To perform a clean build:

```bash
# Remove old build artifacts
rm -rf build/ dist/

# Rebuild
pyinstaller nlp_processor.spec
```

## Support

For PyInstaller-specific issues, consult:
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller GitHub Issues](https://github.com/pyinstaller/pyinstaller/issues)
