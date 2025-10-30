#!/usr/bin/env python3
r"""
Generic Beamer Presentation Generator from Jupyter Notebooks

This script generates LaTeX Beamer presentation code and extracts images,
code cells, and markdown content directly from any Jupyter notebook.

Features:
- Extracts markdown cells for context and structure
- Extracts code cells and saves them as individual Python files
- Provides \CODE{} LaTeX macro for including code snippets
- Extracts all embedded images (PNG/JPG) from notebook outputs
- Automatically inserts images and markdown into the presentation
- Uses Madrid theme with customizable colors
- Organizes all files in presentation/ directory
- Generates cross-platform compilation scripts for macOS, Linux, and Windows
- Works with any Jupyter notebook (language-agnostic)

Usage:
    python generate_presentation.py <notebook_path>
    python generate_presentation.py my_notebook.ipynb

Output:
    - presentation/presentation.tex: LaTeX presentation file
    - presentation/figures/: Directory containing extracted images
    - presentation/code/: Directory containing code cells
    - presentation/compile_presentation.sh: Shell script (macOS/Linux/Git Bash)
    - presentation/compile_presentation.bat: Batch script (Windows)

Using the CODE Macro:
    In your LaTeX file, use \CODE{cell_XXX.ext} to include code:
    \begin{frame}{Code Example}
        \CODE{cell_001.py}
    \end{frame}
"""

import os
import sys
import json
import base64
import re
import shutil
from pathlib import Path
from datetime import datetime


# University Theme Definitions
UNIVERSITY_THEMES = {
    'cu': {
        'name': 'University of Colorado Boulder',
        'primary': (207, 184, 124),    # CU Gold
        'secondary': (0, 0, 0),          # Black
        'tertiary': (86, 90, 92),       # Dark Gray
        'quaternary': (162, 164, 163),   # Light Gray
        'logo': 'cu_logo.png'
    },
    'mit': {
        'name': 'Massachusetts Institute of Technology',
        'primary': (163, 31, 52),       # MIT Red
        'secondary': (138, 139, 140),    # MIT Gray
        'tertiary': (0, 0, 0),          # Black
        'quaternary': (200, 200, 200),   # Light Gray
        'logo': 'mit_logo.png'
    },
    'stanford': {
        'name': 'Stanford University',
        'primary': (140, 21, 21),       # Cardinal Red
        'secondary': (46, 45, 41),       # Cool Gray
        'tertiary': (0, 0, 0),          # Black
        'quaternary': (229, 229, 229),   # Light Gray
        'logo': 'stanford_logo.png'
    },
    'fiu': {
        'name': 'Florida International University',
        'primary': (8, 30, 63),         # FIU Blue
        'secondary': (179, 163, 105),    # FIU Gold
        'tertiary': (0, 0, 0),          # Black
        'quaternary': (200, 200, 200),   # Light Gray
        'logo': 'fiu_logo.png'
    }
}


def ensure_logo_exists(theme, script_dir):
    """Ensure logo file exists, create placeholder if needed."""
    logo_filename = UNIVERSITY_THEMES[theme]['logo']
    logo_path = script_dir / 'assets' / 'logos' / logo_filename

    if not logo_path.exists():
        # Create a simple SVG placeholder logo
        university_name = UNIVERSITY_THEMES[theme]['name']
        primary = UNIVERSITY_THEMES[theme]['primary']

        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="300" height="300" fill="rgb({primary[0]},{primary[1]},{primary[2]})" opacity="0.1"/>
  <text x="150" y="150" font-family="Arial, sans-serif" font-size="24"
        font-weight="bold" text-anchor="middle"
        fill="rgb({primary[0]},{primary[1]},{primary[2]})">
    {university_name.split()[0]}
  </text>
  <text x="150" y="180" font-family="Arial, sans-serif" font-size="18"
        text-anchor="middle"
        fill="rgb({primary[0]},{primary[1]},{primary[2]})">
    {" ".join(university_name.split()[1:])}
  </text>
</svg>'''

        # Save as SVG (LaTeX can include SVG directly with proper packages)
        svg_logo_path = logo_path.with_suffix('.svg')
        with open(svg_logo_path, 'w') as f:
            f.write(svg_content)

        return logo_filename.replace('.png', '.svg')

    return logo_filename


def extract_markdown_cells(notebook_path):
    """
    Extract markdown cells from Jupyter notebook.

    Parameters:
    -----------
    notebook_path : str
        Path to the Jupyter notebook file

    Returns:
    --------
    list of dict
        List of markdown cells with metadata
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Notebook '{notebook_path}' not found.")
        return []

    markdown_cells = []

    for cell_idx, cell in enumerate(notebook['cells']):
        if cell.get('cell_type') == 'markdown':
            # Join all source lines
            content = ''.join(cell.get('source', []))

            markdown_cells.append({
                'cell_index': cell_idx,
                'content': content,
                'type': 'markdown'
            })
            print(f"  Extracted markdown cell {cell_idx}")

    return markdown_cells


def extract_code_cells(notebook_path):
    """
    Extract code cells from Jupyter notebook.

    Parameters:
    -----------
    notebook_path : str
        Path to the Jupyter notebook file

    Returns:
    --------
    list of dict
        List of code cells with metadata
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Notebook '{notebook_path}' not found.")
        return []

    code_cells = []

    for cell_idx, cell in enumerate(notebook['cells']):
        if cell.get('cell_type') == 'code':
            # Join all source lines
            content = ''.join(cell.get('source', []))

            # Skip empty cells
            if content.strip():
                code_cells.append({
                    'cell_index': cell_idx,
                    'content': content,
                    'type': 'code'
                })
                print(f"  Extracted code cell {cell_idx}")

    return code_cells


def extract_images_from_notebook(notebook_path, output_dir='presentation/figures'):
    """
    Extract all images from Jupyter notebook outputs.

    Parameters:
    -----------
    notebook_path : str
        Path to the Jupyter notebook file
    output_dir : str
        Directory to save extracted images

    Returns:
    --------
    list of dict
        List of extracted images with metadata
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load notebook
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Notebook '{notebook_path}' not found.")
        return []

    extracted_images = []
    image_counter = 0

    # Iterate through cells
    for cell_idx, cell in enumerate(notebook['cells']):
        if cell.get('cell_type') != 'code':
            continue

        # Get cell source to understand context
        cell_source = ''.join(cell.get('source', []))

        # Check outputs
        for output in cell.get('outputs', []):
            # Look for display_data or execute_result with images
            if output.get('output_type') in ['display_data', 'execute_result']:
                data = output.get('data', {})

                # Extract PNG images
                if 'image/png' in data:
                    image_counter += 1
                    image_data = data['image/png']

                    # Decode base64
                    image_bytes = base64.b64decode(image_data)

                    # Generate descriptive filename based on context
                    filename = f"figure_{image_counter:03d}.png"

                    # Try to infer what the plot shows
                    plot_type = infer_plot_type(cell_source, image_counter)
                    if plot_type:
                        filename = f"{plot_type}_{image_counter:03d}.png"

                    filepath = os.path.join(output_dir, filename)

                    # Save image
                    with open(filepath, 'wb') as img_file:
                        img_file.write(image_bytes)

                    extracted_images.append({
                        'filename': filename,
                        'filepath': filepath,
                        'cell_index': cell_idx,
                        'plot_type': plot_type,
                        'cell_source': cell_source[:200]  # First 200 chars for context
                    })

                    print(f"  Extracted: {filename}")

    return extracted_images


def infer_plot_type(cell_source, counter):
    """
    Placeholder for plot type inference.

    This function intentionally returns None to keep the script generic.
    Images are named generically as figure_001.png, figure_002.png, etc.

    Parameters:
    -----------
    cell_source : str
        Source code of the cell (unused)
    counter : int
        Image counter for uniqueness (unused)

    Returns:
    --------
    None
        Always returns None for generic naming
    """
    return None


def markdown_to_latex(markdown_text):
    """
    Convert markdown text to LaTeX format.

    Parameters:
    -----------
    markdown_text : str
        Markdown text to convert

    Returns:
    --------
    str
        LaTeX formatted text
    """
    # Remove leading/trailing whitespace
    text = markdown_text.strip()

    # Skip empty cells
    if not text:
        return None

    # First convert headers BEFORE any other processing
    text = re.sub(r'^#####\s+(.*?)$', r'<<<H5>>>\1<<<ENDH5>>>', text, flags=re.MULTILINE)
    text = re.sub(r'^####\s+(.*?)$', r'<<<H4>>>\1<<<ENDH4>>>', text, flags=re.MULTILINE)

    # Convert bold/italic/links BEFORE escaping
    text = re.sub(r'\*\*(.*?)\*\*', r'<<<BOLD>>>\1<<<ENDBOLD>>>', text)
    text = re.sub(r'\*(.*?)\*', r'<<<ITALIC>>>\1<<<ENDITALIC>>>', text)
    text = re.sub(r'`(.*?)`', r'<<<CODE>>>\1<<<ENDCODE>>>', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<<<LINK>>>\2<<<LINKTEXT>>>\1<<<ENDLINK>>>', text)

    # Escape special LaTeX characters EXCEPT those in our placeholders
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Now convert placeholders to LaTeX commands
    text = text.replace('<<<H5>>>', r'\textit{')
    text = text.replace('<<<ENDH5>>>', r'}\\')
    text = text.replace('<<<H4>>>', r'\textbf{')
    text = text.replace('<<<ENDH4>>>', r'}\\')
    text = text.replace('<<<BOLD>>>', r'\textbf{')
    text = text.replace('<<<ENDBOLD>>>', '}')
    text = text.replace('<<<ITALIC>>>', r'\textit{')
    text = text.replace('<<<ENDITALIC>>>', '}')
    text = text.replace('<<<CODE>>>', r'\texttt{')
    text = text.replace('<<<ENDCODE>>>', '}')
    text = text.replace('<<<LINK>>>', r'\href{')
    text = text.replace('<<<LINKTEXT>>>', '}{')
    text = text.replace('<<<ENDLINK>>>', '}')

    # Convert headers (should already be removed at frame level, but just in case)
    text = re.sub(r'^####\s+(.*?)$', r'\\textbf{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.*?)$', r'\\subsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*?)$', r'\\section{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s+(.*?)$', r'\\section{\1}', text, flags=re.MULTILINE)

    # Convert markdown lists to LaTeX itemize
    lines = text.split('\n')
    result_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Check if this is a list item
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result_lines.append('\\begin{itemize}')
                in_list = True
            # Remove the list marker and add \item
            content = stripped[2:].strip()
            result_lines.append(f'    \\item {content}')
        else:
            # Not a list item
            if in_list:
                result_lines.append('\\end{itemize}')
                in_list = False
            if stripped:  # Only add non-empty lines
                result_lines.append(line)

    # Close list if still open
    if in_list:
        result_lines.append('\\end{itemize}')

    text = '\n'.join(result_lines)

    return text


def extract_title_info(markdown_cells):
    """
    Extract title, subtitle, author, and institute from markdown cells.
    Looks for the first H1 or H2 as title, and other metadata.
    """
    title = "Presentation"
    subtitle = ""
    author = "Author"
    institute = "Institute"

    # Try to extract from all markdown cells
    if markdown_cells:
        # Combine all markdown content for better extraction
        all_content = '\n'.join([cell['content'] for cell in markdown_cells])

        # Extract from first cell
        first_cell = markdown_cells[0]['content']
        lines = first_cell.split('\n')

        title_found = False
        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Look for H1 or H2 for title (first occurrence)
            if line_stripped.startswith('## ') and not title_found:
                title = line_stripped.lstrip('## ').strip()
                title_found = True
            elif line_stripped.startswith('# ') and not title_found:
                title = line_stripped.lstrip('# ').strip()
                title_found = True
            # Look for H3 or H4 for subtitle (but skip common ones like "Problem Statement")
            elif line_stripped.startswith('### ') and title_found and not subtitle:
                potential_subtitle = line_stripped.lstrip('### ').strip()
                # Skip generic section headers
                if potential_subtitle.lower() not in ['problem statement', 'objectives', 'introduction',
                                                        'the dataset', 'eda', 'models', 'deliverables']:
                    subtitle = potential_subtitle

        # Search for author name in all content (look for name patterns)
        # Pattern: "I, **Name**," or "by Name" or "Author: Name"
        author_patterns = [
            r'I,?\s+\*\*([^*]+)\*\*,',  # Matches "I, **Name**,"
            r'[Aa]uthor:?\s+([A-Z][a-zA-Z\s]+)',  # Matches "Author: Name"
            r'[Bb]y:?\s+([A-Z][a-zA-Z\s]+)',  # Matches "By: Name"
            r'[Nn]ame:?\s+([A-Z][a-zA-Z\s]+)',  # Matches "Name: Full Name"
        ]

        for pattern in author_patterns:
            match = re.search(pattern, all_content)
            if match:
                author = match.group(1).strip()
                break

        # Search for institute/university in all content
        institute_patterns = [
            r'(University of Colorado Boulder)',
            r'(Colorado Boulder)',
            r'(University of [A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+ University)',
            r'([A-Z][a-zA-Z\s]+ College)',
            r'([A-Z][a-zA-Z\s]+ Institute)',
        ]

        for pattern in institute_patterns:
            match = re.search(pattern, all_content)
            if match:
                institute = match.group(1).strip()
                # Normalize "Colorado Boulder" to full name
                if institute == "Colorado Boulder":
                    institute = "University of Colorado Boulder"
                break

    return {
        'title': title,
        'subtitle': subtitle,
        'author': author,
        'institute': institute
    }


def load_template(script_dir, theme):
    """Load and populate the LaTeX template with theme-specific values."""
    template_path = script_dir / 'templates' / 'beamer_template.tex'

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, 'r') as f:
        template = f.read()

    # Get theme configuration
    theme_config = UNIVERSITY_THEMES.get(theme, UNIVERSITY_THEMES['cu'])

    # Ensure logo exists
    logo_file = ensure_logo_exists(theme, script_dir)

    # Populate placeholders
    replacements = {
        '{{UNIVERSITY_NAME}}': theme_config['name'],
        '{{PRIMARY_R}}': str(theme_config['primary'][0]),
        '{{PRIMARY_G}}': str(theme_config['primary'][1]),
        '{{PRIMARY_B}}': str(theme_config['primary'][2]),
        '{{SECONDARY_R}}': str(theme_config['secondary'][0]),
        '{{SECONDARY_G}}': str(theme_config['secondary'][1]),
        '{{SECONDARY_B}}': str(theme_config['secondary'][2]),
        '{{TERTIARY_R}}': str(theme_config['tertiary'][0]),
        '{{TERTIARY_G}}': str(theme_config['tertiary'][1]),
        '{{TERTIARY_B}}': str(theme_config['tertiary'][2]),
        '{{QUATERNARY_R}}': str(theme_config['quaternary'][0]),
        '{{QUATERNARY_G}}': str(theme_config['quaternary'][1]),
        '{{QUATERNARY_B}}': str(theme_config['quaternary'][2]),
        '{{LOGO_FILE}}': logo_file
    }

    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    return template


def generate_beamer_with_content(images, markdown_cells, code_cells, theme='cu', script_dir=None):
    """
    Generate LaTeX Beamer presentation with extracted images, markdown, and code.
    Completely generic - reads ALL content from the notebook.

    Parameters:
    -----------
    theme : str
        University theme key ('cu', 'mit', 'stanford', 'fiu')

    Other Parameters:
    -----------
    images : list of dict
        List of extracted images with metadata
    markdown_cells : list of dict
        List of markdown cells with content
    code_cells : list of dict
        List of code cells with content

    Returns:
    --------
    str
        Complete LaTeX code
    """

    # Extract title information from markdown
    title_info = extract_title_info(markdown_cells)

    # Load template and populate with theme/title info
    if script_dir is None:
        script_dir = Path(__file__).parent

    template = load_template(script_dir, theme)

    # Populate title information
    subtitle_line = f"\\subtitle{{{title_info['subtitle']}}}" if title_info['subtitle'] else ""

    template = template.replace('{{TITLE}}', title_info['title'])
    template = template.replace('{{SUBTITLE}}', subtitle_line)
    template = template.replace('{{AUTHOR}}', title_info['author'])
    template = template.replace('{{INSTITUTE}}', title_info['institute'])

    # Create mappings by cell index for proper ordering
    images_by_cell = {}
    for img in images:
        cell_idx = img['cell_index']
        if cell_idx not in images_by_cell:
            images_by_cell[cell_idx] = []
        images_by_cell[cell_idx].append(img)

    # Create mapping for code cells
    code_by_cell = {}
    for code in code_cells:
        cell_idx = code['cell_index']
        code_by_cell[cell_idx] = code

    # Build content section
    content_latex = ""

    # Create a unified timeline of all cells (markdown, code, images)
    # We'll process cells in order and add appropriate frames
    all_cell_indices = set()
    all_cell_indices.update([mc['cell_index'] for mc in markdown_cells])
    all_cell_indices.update([cc['cell_index'] for cc in code_cells])
    all_cell_indices.update(images_by_cell.keys())

    # Process cells in order
    for cell_idx in sorted(all_cell_indices):
        # Check if this is a markdown cell
        md_cell = next((mc for mc in markdown_cells if mc['cell_index'] == cell_idx), None)
        if md_cell:
            content = md_cell['content'].strip()
            if content:
                # Split content into sections based on headers
                lines = content.split('\n')

                current_frame_content = []
                current_frame_title = None
                in_frame = False

                for line in lines:
                    line_stripped = line.strip()

                    # Check for section header (# or ##)
                    if line_stripped.startswith('## '):
                        # Close previous frame if open
                        if in_frame and current_frame_content:
                            content_latex += convert_markdown_to_frame(current_frame_title, '\n'.join(current_frame_content))
                            current_frame_content = []

                        # Add section
                        section_title = line_stripped.lstrip('## ').strip()
                        content_latex += f"\n\\section{{{section_title}}}\n\n"
                        in_frame = False
                        current_frame_title = None

                    elif line_stripped.startswith('### '):
                        # Close previous frame if open
                        if in_frame and current_frame_content:
                            content_latex += convert_markdown_to_frame(current_frame_title, '\n'.join(current_frame_content))
                            current_frame_content = []

                        # Start new frame with this as title
                        current_frame_title = line_stripped.lstrip('### ').strip()
                        in_frame = True

                    elif line_stripped.startswith('# '):
                        # Close previous frame if open
                        if in_frame and current_frame_content:
                            content_latex += convert_markdown_to_frame(current_frame_title, '\n'.join(current_frame_content))
                            current_frame_content = []

                        # Add section
                        section_title = line_stripped.lstrip('# ').strip()
                        content_latex += f"\n\\section{{{section_title}}}\n\n"
                        in_frame = False
                        current_frame_title = None

                    elif line_stripped.startswith('---'):
                        # Separator - close frame if open
                        if in_frame and current_frame_content:
                            content_latex += convert_markdown_to_frame(current_frame_title, '\n'.join(current_frame_content))
                            current_frame_content = []
                            in_frame = False
                            current_frame_title = None

                    else:
                        # Regular content - add to current frame
                        if not in_frame and line_stripped:
                            # Start a new frame without explicit title
                            in_frame = True
                            current_frame_title = ""

                        if in_frame:
                            current_frame_content.append(line)

                # Close final frame if open
                if in_frame and current_frame_content:
                    content_latex += convert_markdown_to_frame(current_frame_title, '\n'.join(current_frame_content))

        # Check if this is a code cell
        if cell_idx in code_by_cell:
            code_cell = code_by_cell[cell_idx]
            # Add a frame with the code
            filename = f"cell_{cell_idx:03d}.py"
            num_lines = code_cell['content'].count('\n') + 1

            # Skip extremely large cells (>200 lines) that would crash LaTeX
            # These are typically class definitions or utility code
            if num_lines > 200:
                content_latex += f"""
\\begin{{frame}}{{Code: Cell {cell_idx} (Large File - {num_lines} lines)}}
    \\textbf{{Note:}} This code cell is very large and has been excluded from the presentation.

    \\vspace{{1em}}

    The complete code is available in: \\texttt{{code/{filename}}}

    \\vspace{{1em}}

    \\begin{{block}}{{Summary}}
    This cell contains substantial implementation code that is better reviewed
    in the source file rather than displayed in presentation slides.
    \\end{{block}}
\\end{{frame}}

"""
            elif num_lines > 50:
                # For large cells (50-200 lines), use allowframebreaks to split across slides
                content_latex += f"""
\\begin{{frame}}[fragile,allowframebreaks]{{Code: Cell {cell_idx}}}
    \\begin{{figure}}
        \\CODE{{{filename}}}
        \\caption{{Code from Cell {cell_idx}}}
    \\end{{figure}}
\\end{{frame}}

"""
            else:
                # Normal size cells - single frame
                content_latex += f"""
\\begin{{frame}}[fragile]{{Code: Cell {cell_idx}}}
    \\begin{{figure}}
        \\CODE{{{filename}}}
        \\caption{{Code from Cell {cell_idx}}}
    \\end{{figure}}
\\end{{frame}}

"""

        # Check if this cell has images (code outputs)
        if cell_idx in images_by_cell:
            for img in images_by_cell[cell_idx]:
                plot_type = img.get('plot_type', 'Result')
                title = plot_type.replace('_', ' ').title() if plot_type else "Analysis Result"
                caption = title if plot_type else f"Output from Cell {cell_idx}"
                content_latex += f"""
\\begin{{frame}}{{{title}}}
    \\begin{{figure}}
        \\centering
        \\includegraphics[width=0.85\\textwidth,height=0.7\\textheight,keepaspectratio]{{assets/figures/{img['filename']}}}
        \\caption{{{caption}}}
    \\end{{figure}}
\\end{{frame}}

"""

    # Insert content into template
    final_latex = template.replace('{{CONTENT}}', content_latex)

    return final_latex


def convert_markdown_to_frame(title, content):
    """
    Convert markdown content to a LaTeX Beamer frame.

    Parameters:
    -----------
    title : str
        Frame title (can be empty)
    content : str
        Markdown content to convert

    Returns:
    --------
    str
        LaTeX frame code
    """
    if not content.strip():
        return ""

    # Convert markdown to LaTeX
    latex_text = markdown_to_latex(content)

    if not latex_text:
        return ""

    # Build frame
    frame_header = f"\\begin{{frame}}{{{title}}}\n" if title else "\\begin{frame}\n"

    frame = frame_header
    frame += latex_text + "\n"
    frame += "\\end{frame}\n\n"

    return frame


def save_code_cells_to_files(code_cells, output_dir='presentation/code'):
    """
    Save code cells to individual Python files for inclusion in LaTeX.

    Parameters:
    -----------
    code_cells : list of dict
        List of code cells with content
    output_dir : str
        Directory to save code files

    Returns:
    --------
    list of dict
        List of saved code files with metadata
    """
    # Create code directory
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []

    for code_cell in code_cells:
        # Create filename based on cell index
        filename = f"cell_{code_cell['cell_index']:03d}.py"
        filepath = os.path.join(output_dir, filename)

        # Save code to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code_cell['content'])

        saved_files.append({
            'filename': filename,
            'filepath': filepath,
            'cell_index': code_cell['cell_index']
        })

        print(f"  Saved: {filename}")

    return saved_files


def save_presentation(content, output_file='presentation/esg_presentation.tex'):
    """Save the LaTeX content to a file."""
    # Create presentation directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Presentation saved to: {output_file}")


def create_compile_script(output_dir='presentation', script_dir=None):
    """Create cross-platform compilation scripts (shell and batch) for LaTeX presentation."""

    if script_dir is None:
        script_dir = Path(__file__).parent

    # Load shell script template
    shell_template_path = script_dir / 'templates' / 'compile_presentation.sh'
    if not shell_template_path.exists():
        raise FileNotFoundError(f"Shell script template not found: {shell_template_path}")

    with open(shell_template_path, 'r', encoding='utf-8') as f:
        shell_script_content = f.read()

    # Load batch script template
    batch_template_path = script_dir / 'templates' / 'compile_presentation.bat'
    if not batch_template_path.exists():
        raise FileNotFoundError(f"Batch script template not found: {batch_template_path}")

    with open(batch_template_path, 'r', encoding='utf-8') as f:
        batch_script_content = f.read()

    # Save shell script
    shell_script_path = os.path.join(output_dir, 'compile_presentation.sh')
    with open(shell_script_path, 'w', encoding='utf-8') as f:
        f.write(shell_script_content)
    os.chmod(shell_script_path, 0o755)
    print(f"✓ Shell script created: {shell_script_path} (macOS/Linux/Git Bash)")

    # Save batch script
    batch_script_path = os.path.join(output_dir, 'compile_presentation.bat')
    with open(batch_script_path, 'w', encoding='utf-8') as f:
        f.write(batch_script_content)
    print(f"✓ Batch script created: {batch_script_path} (Windows)")


def main():
    """Main execution function."""

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_presentation.py <notebook_path> [theme]")
        print("Example: python generate_presentation.py my_notebook.ipynb cu")
        print("\nAvailable themes:")
        for key, config in UNIVERSITY_THEMES.items():
            print(f"  {key:10s} - {config['name']}")
        print("\nDefault theme: cu (University of Colorado Boulder)")
        sys.exit(1)

    notebook_path = sys.argv[1]
    theme = sys.argv[2] if len(sys.argv) > 2 else 'cu'

    # Validate theme
    if theme not in UNIVERSITY_THEMES:
        print(f"Error: Unknown theme '{theme}'")
        print("Available themes:", ", ".join(UNIVERSITY_THEMES.keys()))
        sys.exit(1)

    # Verify notebook exists
    if not os.path.exists(notebook_path):
        print(f"Error: Notebook '{notebook_path}' not found.")
        sys.exit(1)

    # Get script directory
    script_dir = Path(__file__).parent

    theme_name = UNIVERSITY_THEMES[theme]['name']
    print("="*80)
    print("Generic Beamer Presentation Generator from Jupyter Notebooks")
    print(f"Theme: {theme_name}")
    print("="*80)
    print(f"Input notebook: {notebook_path}")
    print()

    # Create presentation directory with new structure
    output_dir = script_dir / 'output'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir / 'assets' / 'figures', exist_ok=True)
    os.makedirs(output_dir / 'assets' / 'code', exist_ok=True)

    # Extract markdown cells
    print("Step 1: Extracting markdown cells from Jupyter notebook...")
    markdown_cells = extract_markdown_cells(notebook_path)
    print(f"✓ Extracted {len(markdown_cells)} markdown cells\n")

    # Extract code cells
    print("Step 2: Extracting code cells from Jupyter notebook...")
    code_cells = extract_code_cells(notebook_path)
    print(f"✓ Extracted {len(code_cells)} code cells\n")

    # Save code cells to external files
    print("Step 3: Saving code cells to external files...")
    saved_code_files = save_code_cells_to_files(code_cells, str(output_dir / 'assets' / 'code'))
    print(f"✓ Saved {len(saved_code_files)} code files\n")

    # Extract images from notebook
    print("Step 4: Extracting images from Jupyter notebook...")
    images = extract_images_from_notebook(notebook_path, str(output_dir / 'assets' / 'figures'))
    print(f"✓ Extracted {len(images)} images\n")

    if not images:
        print("Warning: No images found in notebook. Generating presentation without images...")

    # Generate LaTeX content with images, markdown, and code
    print("Step 5: Generating LaTeX Beamer presentation...")
    latex_content = generate_beamer_with_content(images, markdown_cells, code_cells, theme, script_dir)

    # Save presentation
    save_presentation(latex_content, str(output_dir / 'presentation.tex'))
    print()

    # Create compile script
    print("Step 6: Creating compilation script...")
    create_compile_script(str(output_dir), script_dir)

    # Copy logo assets to output directory
    logo_src = script_dir / 'assets' / 'logos'
    logo_dst = output_dir / 'assets' / 'logos'
    if logo_src.exists():
        shutil.copytree(logo_src, logo_dst, dirs_exist_ok=True)
    print()

    # Summary
    print("="*80)
    print("✓ DONE! All files generated successfully.")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  - output/presentation.tex (LaTeX source)")
    print(f"  - output/assets/figures/ ({len(images)} extracted images)")
    print(f"  - output/assets/code/ ({len(code_cells)} code files)")
    print(f"  - output/assets/logos/ (University logo)")
    print(f"  - output/compile_presentation.sh (Shell script for macOS/Linux/Git Bash)")
    print(f"  - output/compile_presentation.bat (Batch script for Windows)")

    if markdown_cells:
        print(f"\nMarkdown cells processed: {len(markdown_cells)}")

    print(f"\nExtracted content:")
    print(f"  - {len(images)} images")
    print(f"  - {len(code_cells)} code cells")

    # Automatically compile the presentation
    print("\n" + "="*80)
    print("Step 7: Compiling presentation...")
    print("="*80)

    import subprocess
    import platform

    # Detect OS and run appropriate compile script
    current_os = platform.system()
    compile_success = False

    # Check if Tectonic is available (for Windows primarily)
    if current_os == 'Windows':
        print("\nChecking for LaTeX compiler...")
        tectonic_check = subprocess.run(['where', 'tectonic'],
                                       capture_output=True,
                                       text=True)

        if tectonic_check.returncode != 0:
            print("Tectonic not found. Checking for Scoop package manager...")
            scoop_check = subprocess.run(['where', 'scoop'],
                                        capture_output=True,
                                        text=True)

            if scoop_check.returncode == 0:
                print("Found Scoop! Installing Tectonic automatically...")
                install_result = subprocess.run(['scoop', 'install', 'tectonic'],
                                              capture_output=False)
                if install_result.returncode == 0:
                    print("✓ Tectonic installed successfully!")
                else:
                    print("⚠ Failed to auto-install Tectonic.")
                    print("Please run: install_tectonic.bat")
                    print("\nOr manually install:")
                    print("   scoop install tectonic")
                    print("   OR")
                    print("   choco install tectonic")
            else:
                print("\n⚠ Tectonic LaTeX compiler not found!")
                print("\nTo compile presentations on Windows, please install Tectonic:")
                print("   1. Run: install_tectonic.bat (in this directory)")
                print("   2. Or install Scoop: https://scoop.sh")
                print("      Then run: scoop install tectonic")
                print("   3. Or install Chocolatey, then: choco install tectonic")
                print("\nAlternatively, install MiKTeX: https://miktex.org/download")
                print("\nAfter installation, run the presentation generator again.")
                return

    try:
        if current_os == 'Windows':
            # Windows - use Tectonic via batch script
            print("\nCompiling with Tectonic...")
            result = subprocess.run(
                ['compile_presentation.bat', 'presentation.tex'],
                cwd=str(output_dir),
                capture_output=False,
                text=True
            )
            compile_success = result.returncode == 0
        else:
            # macOS, Linux, or other Unix-like systems
            print(f"\nDetected {current_os} - compiling with pdflatex...")
            result = subprocess.run(
                ['./compile_presentation.sh', 'presentation.tex'],
                cwd=str(output_dir),
                capture_output=False,
                text=True
            )
            compile_success = result.returncode == 0

        if compile_success:
            print("\n" + "="*80)
            print("✓ PDF compilation successful!")
            print("="*80)
            print(f"\nFinal output: output/presentation.pdf")
        else:
            print("\n" + "="*80)
            print("⚠ PDF compilation encountered issues")
            print("="*80)
            print("\nPlease check the output above for errors.")
            print("\nYou can manually re-compile using:")
            if current_os == 'Windows':
                print("   cd output")
                print("   compile_presentation.bat presentation.tex")
            else:
                print("   cd output")
                print("   ./compile_presentation.sh presentation.tex")
    except FileNotFoundError as e:
        print(f"\n⚠ Compilation tool not found: {e}")
        if current_os == 'Windows':
            print("\nFor Windows, please install Tectonic:")
            print("   Run: install_tectonic.bat")
            print("   Or: scoop install tectonic")
        else:
            print("\nPlease install LaTeX distribution:")
            print("   - macOS: brew install --cask mactex")
            print("   - Linux: sudo apt-get install texlive-full")
    except Exception as e:
        print(f"\n⚠ Compilation error: {e}")
        print("\nYou can manually compile using:")
        if current_os == 'Windows':
            print("   cd output && compile_presentation.bat presentation.tex")
        else:
            print("   cd output && ./compile_presentation.sh presentation.tex")

    print("\n" + "="*80)
    print("All images, markdown content, and code cells have been automatically extracted!")
    print("Code files are available in output/assets/code/ directory for inclusion via \\CODE{} macro.")
    print("="*80)


if __name__ == "__main__":
    main()
