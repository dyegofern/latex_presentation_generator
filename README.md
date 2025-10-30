# LaTeX Beamer Presentation Generator

A generic Beamer presentation generator that extracts content from Jupyter notebooks and creates LaTeX presentations with customizable university themes.

## Features

- **Generic & Notebook-Agnostic**: Works with any Jupyter notebook regardless of content type
- **Multi-University Themes**: Supports CU Boulder, MIT, Stanford, and FIU with official color schemes
- **Template-Based**: Uses external LaTeX templates for easy customization
- **Logo Support**: Automatically includes university logos (with placeholder generation if not available)
- **Asset Organization**: Clean directory structure with all assets (code, figures, logos) organized
- **Cross-Platform**: Generates compilation scripts for macOS, Linux, and Windows

## Directory Structure

```
presentation_generator/
├── generate_presentation.py    # Main script
├── templates/
│   └── beamer_template.tex     # LaTeX Beamer template
├── assets/
│   └── logos/                  # University logos
│       ├── README.md           # Logo installation guide
│       ├── cu_logo.png         # CU Boulder logo
│       ├── mit_logo.png        # MIT logo
│       ├── stanford_logo.png   # Stanford logo
│       └── fiu_logo.png        # FIU logo
└── output/                     # Generated presentation (created on run)
    ├── presentation.tex        # Generated LaTeX source
    ├── presentation.pdf        # Compiled PDF (after running compile script)
    ├── compile_presentation.sh # Unix compilation script
    ├── compile_presentation.bat# Windows compilation script
    └── assets/
        ├── code/               # Extracted code cells
        ├── figures/            # Extracted images
        └── logos/              # Copied university logos
```

## Installation

1. **Requirements**:
   - Python 3.6+
   - LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
   - Standard Python libraries (json, base64, pathlib)

2. **Optional - Download University Logos**:
   - See `assets/logos/README.md` for official logo sources
   - Logos should be PNG or SVG format
   - Place in `assets/logos/` directory
   - If logos are missing, placeholder SVGs will be generated automatically

## Usage

### Basic Usage

```bash
cd presentation_generator
python3 generate_presentation.py <notebook_path> [theme]
```

### Examples

```bash
# Generate with CU Boulder theme (default)
python3 generate_presentation.py my_notebook.ipynb

# Generate with MIT theme
python3 generate_presentation.py my_notebook.ipynb mit

# Generate with Stanford theme
python3 generate_presentation.py my_notebook.ipynb stanford

# Generate with FIU theme
python3 generate_presentation.py my_notebook.ipynb fiu
```

### Compile Presentation

After generation, compile the presentation:

**macOS/Linux:**
```bash
cd output
./compile_presentation.sh presentation.tex
```

**Windows:**
```cmd
cd output
compile_presentation.bat presentation.tex
```

### View Results

The compiled PDF will be at `output/presentation.pdf`

## Available Themes

| Theme Key | University | Primary Color |
|-----------|------------|---------------|
| `cu` | University of Colorado Boulder | Gold (207, 184, 124) |
| `mit` | Massachusetts Institute of Technology | Red (163, 31, 52) |
| `stanford` | Stanford University | Cardinal Red (140, 21, 21) |
| `fiu` | Florida International University | Blue (8, 30, 63) |

## Customization

### Adding New Themes

Edit `generate_presentation.py` and add to the `UNIVERSITY_THEMES` dictionary:

```python
'mytheme': {
    'name': 'My University',
    'primary': (R, G, B),      # Primary color
    'secondary': (R, G, B),    # Secondary color
    'tertiary': (R, G, B),     # Tertiary color
    'quaternary': (R, G, B),   # Quaternary color
    'logo': 'mytheme_logo.png' # Logo filename
}
```

Then add the logo file to `assets/logos/`.

### Customizing the LaTeX Template

Edit `templates/beamer_template.tex` to customize:
- Beamer theme and color schemes
- Font styles and sizes
- Package imports
- Footer/header layouts
- Code listing styles

Placeholders available in template:
- `{{UNIVERSITY_NAME}}` - University full name
- `{{PRIMARY_R}}`, `{{PRIMARY_G}}`, `{{PRIMARY_B}}` - Primary color RGB
- `{{SECONDARY_R}}`, `{{SECONDARY_G}}`, `{{SECONDARY_B}}` - Secondary color RGB
- `{{TERTIARY_R}}`, `{{TERTIARY_G}}`, `{{TERTIARY_B}}` - Tertiary color RGB
- `{{QUATERNARY_R}}`, `{{QUATERNARY_G}}`, `{{QUATERNARY_B}}` - Quaternary color RGB
- `{{LOGO_FILE}}` - Logo filename
- `{{TITLE}}` - Presentation title
- `{{SUBTITLE}}` - Presentation subtitle
- `{{AUTHOR}}` - Author name
- `{{INSTITUTE}}` - Institution name
- `{{CONTENT}}` - Generated presentation content

## Features in Detail

### Automatic Content Extraction

The script automatically extracts and processes:
- **Markdown cells**: Converted to Beamer frames with sections/subsections
- **Code cells**: Saved as individual `.py` files in `assets/code/`
- **Images**: Extracted as PNG files in `assets/figures/`
- **Metadata**: Title, author, institution from first markdown cell

### Code Inclusion

Use the `\CODE{}` macro in LaTeX to include code:

```latex
\begin{frame}{My Code}
    \CODE{cell_001.py}
\end{frame}
```

### Logo Handling

- If logo file exists in `assets/logos/`, it will be used
- If logo is missing, a placeholder SVG is automatically generated
- Logo appears on title slide via `\titlegraphic`
- Recommended logo size: 300x300px minimum

## Troubleshooting

### Compilation Errors

1. **LaTeX errors**: Check `output/presentation.log` for details
2. **Missing packages**: Install required LaTeX packages (listings, xcolor, graphicx, etc.)
3. **SVG logos not working**: Some LaTeX distributions require `svg` package

### Script Errors

1. **Template not found**: Ensure `templates/beamer_template.tex` exists
2. **Notebook not found**: Check notebook path is correct
3. **Permission errors**: Ensure write permissions for output directory

## License

This tool is provided as-is for academic and educational use.

## Credits

Supports presentations for:
- University of Colorado Boulder
- Massachusetts Institute of Technology
- Stanford University
- Florida International University

Official university logos and colors are property of their respective institutions.
