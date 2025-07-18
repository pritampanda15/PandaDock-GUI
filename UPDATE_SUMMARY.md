# PandaDOCK GUI Updates - New CLI Interface Integration

## Overview
Successfully updated the PandaDOCK GUI to use the new pandadock command-line interface with modern algorithms and scoring functions.

## Major Updates

### 1. New Algorithm Templates
Replaced old algorithm templates with new ones based on the latest pandadock CLI:

- **Fast Mode - PandaCore**: `--mode fast --scoring pandacore --num-poses 9 --exhaustiveness 8`
- **Balanced Mode - PandaML**: `--mode balanced --scoring pandaml --num-poses 20 --exhaustiveness 16 --ml-rescoring`
- **Precise Mode - PandaPhysics**: `--mode precise --scoring pandaphysics --num-poses 50 --exhaustiveness 32 --side-chain-flexibility`
- **Virtual Screening - Fast**: `--mode fast --scoring pandacore --num-poses 5 --exhaustiveness 4 --save-poses`
- **Virtual Screening - Balanced**: `--mode balanced --scoring pandaml --num-poses 10 --exhaustiveness 8 --ml-rescoring --save-poses`
- **High-Precision Docking**: `--mode precise --scoring pandaphysics --num-poses 100 --exhaustiveness 64 --side-chain-flexibility --save-complex`
- **Flexible Residue Docking**: `--mode balanced --scoring pandaml --num-poses 20 --exhaustiveness 16 --side-chain-flexibility --ml-rescoring`
- **GPU-Accelerated Docking**: `--mode fast --scoring pandacore --num-poses 20 --exhaustiveness 16 --gpu`
- **Complete Analysis Suite**: `--mode balanced --scoring pandaml --num-poses 20 --exhaustiveness 16 --ml-rescoring --pandamap --pandamap-3d --all-outputs --plots --interaction-maps`
- **Metal Complex Docking**: `--mode precise --scoring pandaphysics --num-poses 50 --exhaustiveness 32 --side-chain-flexibility --save-complex --pandamap`

### 2. Updated Command Line Interface
Updated all command execution functions to use the new CLI structure:

#### Single Ligand Docking
- Changed from `-l` to `--ligand`
- Changed from `-p` to `--protein`
- Changed from `-o` to `--out`
- Changed from `-s` to `--center`
- Added `--size` parameter for box dimensions
- Removed `--grid-radius` (replaced with `--size`)

#### Virtual Screening
- Changed from `--ligand-library` to `--screen`
- Updated parameter structure for consistency

### 3. New Scoring Functions
- **PandaCore**: Fast, traditional scoring
- **PandaML**: Machine learning enhanced scoring with rescoring
- **PandaPhysics**: Physics-based scoring for metal complexes and precise calculations

### 4. Enhanced Features
- **Flexible Residue Support**: Added `--flexible-residues` parameter support
- **GPU Acceleration**: Simplified to `--gpu` flag
- **Advanced Analysis**: Integrated PandaMap visualization (`--pandamap`, `--pandamap-3d`)
- **Comprehensive Outputs**: Added `--all-outputs`, `--plots`, `--interaction-maps`

### 5. Updated Workflow Logic
- Improved virtual screening detection
- Better handling of pocket detection vs manual site definition
- Enhanced command generation with flexible residue support

## New CLI Parameters Supported

### Core Parameters
- `--mode {fast,balanced,precise}`: Docking mode
- `--scoring {pandacore,pandaml,pandaphysics}`: Scoring function
- `--num-poses`: Number of poses to generate
- `--exhaustiveness`: Search exhaustiveness
- `--center X Y Z`: Binding site center coordinates
- `--size X Y Z`: Search box dimensions

### Advanced Parameters
- `--ml-rescoring`: Enable ML rescoring
- `--side-chain-flexibility`: Enable flexible side chains
- `--flexible-residues`: Specify flexible residues
- `--gpu`: Enable GPU acceleration
- `--save-poses`: Save all poses
- `--save-complex`: Save protein-ligand complex

### Analysis Parameters
- `--pandamap`: Generate interaction maps
- `--pandamap-3d`: Generate 3D interaction maps
- `--all-outputs`: Generate all output formats
- `--plots`: Generate analysis plots
- `--interaction-maps`: Generate interaction maps

## Installation Requirements

The updated GUI requires the new pandadock CLI tool to be installed:

```bash
# Install from PyPI
pip install pandadock

# Or install from source
git clone https://github.com/pritampanda15/pandadock.git
cd pandadock
pip install -e .[all]
```

## Dependencies Fixed

1. **Syntax Errors**: Fixed all Python 2/3 compatibility issues
2. **PySide6**: Successfully installed and configured
3. **RDKit**: Installed for molecular operations
4. **BioPython**: Installed for PDB handling
5. **PyMOL**: Configured for visualization
6. **OpenBabel**: Installed for chemical format conversion
7. **PLIP**: Installed for protein-ligand interaction analysis
8. **APSW**: Installed for SQLite operations
9. **MolKit**: Created mock replacement for Python 3 compatibility

## Testing
The GUI launches successfully and is ready for use with the new pandadock CLI interface.

## Future Enhancements
- Add support for custom configuration files (`--config`, `--save-config`)
- Implement flexible residue selection interface
- Add support for multiple output formats
- Enhance GPU detection and configuration
