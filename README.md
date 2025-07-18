# PandaDOCK GUI

PandaDock GUI application for molecular docking using PandaDock algorithms.


## Features

- Molecular visualization using PyMOL
- Molecular docking capabilities
- Interactive GUI with PySide6
- Support for various molecular file formats (PDB, SDF)
- Grid box visualization and manipulation
- Molecular plugin system

## Prerequisites

- Python 3.9 or higher
- Conda (recommended for environment management)

## Installation

### Option 1: Using Conda (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PandaDockGUI.git
cd PandaDockGUI
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate pandadock
```

3. Run the application:
```bash
python PandaDOCK.py
```

### Option 2: Using pip

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PandaDockGUI.git
cd PandaDockGUI
```

2. Create a virtual environment:
```bash
python -m venv pandadock_env
source pandadock_env/bin/activate  # On Windows: pandadock_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python PandaDOCK.py
```

## Usage

1. Launch the application by running `python PandaDOCK.py`
2. Load your protein structure files (PDB format) using the File menu
3. Load ligand files (SDF format) for docking
4. Configure docking parameters using the interface
5. Run docking simulations
6. Visualize results in the PyMOL viewer


## Dependencies

- **PySide6**: GUI framework
- **PyMOL**: Molecular visualization
- **RDKit**: Cheminformatics toolkit
- **BioPython**: Biological computation
- **NumPy**: Numerical computing
- **Pillow**: Image processing
- **PLIP**: Protein-ligand interaction profiler

## Test Data

The `Test/` directory contains sample data for testing:
- `Test/Protein/`: Sample protein PDB files
- `Test/Ligand/`: Sample ligand SDF files
- `Test/Heteroatoms/`: Heteroatom files for testing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **PyMOL not found**: Ensure PyMOL is properly installed via conda
2. **Qt platform plugin issues**: Check that PySide6 is correctly installed
3. **Import errors**: Verify all dependencies are installed in the correct environment

### Support

For issues and questions, please open an issue on the GitHub repository.