# koios/chronicler_module/renderer.py
"""Renders the analyzed data and generated content into the final output format (HTML)."""

import os
from pathlib import Path
from datetime import datetime
import html # Import the html module for escaping
import logging # Import logging

# --- Logger Setup ---
logger = logging.getLogger(__name__)

def render_to_html(analysis_data: dict, generated_summary: str, output_dir: str = None) -> str | None:
    """
    Renders the analysis data and summary into an HTML file with embedded CSS.

    Args:
        analysis_data: The dictionary from the analyzer.
        generated_summary: The summary string from the generator.
        output_dir: Optional directory to save the HTML file. If None, returns HTML string.

    Returns:
        The path to the generated HTML file if output_dir is specified,
        otherwise the HTML content as a string.
        Returns None on error.
    """
    logger.info("Starting HTML rendering process...")
    logger.debug(">>> DEBUG: Entering Renderer: render_to_html") # Debug

    try:
        # Extract data safely
        project_name = html.escape(analysis_data.get('project_name', 'Unknown Project'))
        languages = analysis_data.get('detected_languages', {})
        total_files = analysis_data.get('total_files_scanned', 0) # Key depends on analyzer output
        key_items = analysis_data.get('key_items', [])
        errors = analysis_data.get('errors', [])

        # Handle summary display - assume generator prefixes with '[ERROR]'
        is_summary_error = generated_summary.startswith('[ERROR]')
        summary_display = html.escape(generated_summary).replace('\n', '<br>\n')
        if is_summary_error:
             summary_html = '<i>AI summary generation failed. See details below.</i>'
             generator_error_html = f'''
             <h2>Generator Output/Error:</h2>
             <ul class="error">
                 <li>{summary_display}</li>
             </ul>'''
        else:
            summary_html = f'<p>{summary_display}</p>'
            generator_error_html = ''

        # Format lists for HTML
        languages_html = ''.join(f'<li>{html.escape(lang)}: {count} file(s)</li>' for lang, count in languages.items()) if languages else '<li>None detected</li>'
        key_items_html = ''.join(f'<li><code>{html.escape(item)}</code></li>' for item in key_items) if key_items else '<li>None specifically identified</li>'
        errors_html = ''.join(f'<li>{html.escape(err)}</li>' for err in errors) if errors else ''
        analysis_errors_section = f'''
        <h2>Errors Encountered During Analysis:</h2>
        <ul class="error">
            {errors_html}
        </ul>''' if errors_html else ''

        generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Start HTML Construction ---
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EGOS Chronicler Summary: {project_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #212529;
        }}
        .container {{
            max-width: 900px;
            margin: 2em auto;
            padding: 2em;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        h1, h2 {{
            color: #343a40;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 0.3em;
            margin-bottom: 0.8em;
        }}
        h1 {{
            font-size: 2em;
        }}
        h2 {{
            font-size: 1.5em;
            margin-top: 1.5em;
        }}
        .summary {{
            background-color: #e9ecef;
            border-left: 5px solid #0d6efd;
            padding: 1em 1.5em;
            margin-bottom: 1.5em;
            border-radius: 4px;
            white-space: pre-wrap; /* Allow line breaks in summary */
        }}
        .summary p, .summary i {{
            margin: 0;
            font-size: 1.1em;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        li {{
            margin-bottom: 0.5em;
            padding: 0.3em 0;
        }}
        code {{
            background-color: #e9ecef;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
            font-size: 0.9em;
        }}
        .error {{
            color: #dc3545;
        }}
        .error li {{
             background-color: #f8d7da; /* Light red background for error items */
             border-left: 3px solid #dc3545;
             padding: 0.5em;
             margin-left: 1em; /* Indent error items */
             list-style: disc; /* Use bullet points for errors */
             margin-bottom: 0.3em;
        }}
        .metadata {{
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 2em;
            border-top: 1px solid #dee2e6;
            padding-top: 1em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>EGOS Chronicler Summary: {project_name}</h1>

        <h2>AI Generated Summary</h2>
        <div class="summary">
            {summary_html}
        </div>

        <h2>Analysis Results</h2>
        <ul>
            <li><strong>Total Files Analyzed:</strong> {total_files}</li>
        </ul>

        <h3>Detected Languages:</h3>
        <ul>
            {languages_html}
        </ul>

        <h3>Key Items Found:</h3>
        <ul>
            {key_items_html}
        </ul>

        {analysis_errors_section}

        {generator_error_html}


        <div class="metadata">
            Report generated by EGOS Chronicler on {generation_time}.
        </div>
    </div>
</body>
</html>
"""
        # --- End HTML Construction ---

        if output_dir:
            output_path = Path(output_dir).resolve() # Ensure absolute path
            try:
                 output_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                 logger.error(f"ERROR: Could not create output directory '{output_path}': {e}")
                 return None # Cannot write file if dir creation fails

            safe_project_name = html.escape(project_name)
            # Sanitize project name for use in filename
            filename_safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(' ', '_').lower()
            # Ensure the filename follows the pattern chronicler_report_{sanitized_name}.html
            report_filename = f"chronicler_report_{filename_safe_project_name}.html"

            output_file_path = output_path / report_filename
            try:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Successfully wrote HTML output to: {output_file_path}")
                logger.debug(">>> DEBUG: Exiting Renderer: render_to_html (File Written)") # Debug
                return str(output_file_path)
            except Exception as e:
                logger.error(f"ERROR: Could not write HTML file: {e}")
                return None
        else:
             logger.debug(">>> DEBUG: Exiting Renderer: render_to_html (String Returned)") # Debug
             return html_content

    except Exception as e:
        logger.critical(f"!!! UNEXPECTED ERROR in Renderer: {e}")
        import traceback
        traceback.print_exc()
        return None
