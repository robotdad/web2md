Here's an updated README for your `web2md.py` script:

```markdown
# Web2MD

Web2MD is a Python script that downloads a web page and converts it into a Markdown document. The script is designed to preserve the structure of the original webpage while including images, without following any links.

## Features

- Downloads a single web page and converts it to Markdown format
- Saves the Markdown file with images in an organized directory structure
- Uses a date-based folder structure for each conversion
- Optionally configurable output directory via an environment variable

## Requirements

- Python 3.10+
- `requests` and `beautifulsoup4` Python libraries

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/robotdad/web2md.git
   cd web2md
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\Activate.ps1
     ```
   - On macOS and Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install requests beautifulsoup4
   ```

## Configuration

### Environment Variables (.env)

- `BASE_OUTPUT_DIR`: Optional. The base directory where converted web pages will be saved. If not set, output defaults to `output/<date>/<domain>/` in the current working directory.

## Usage

Ensure your virtual environment is activated, then run the script with:

```bash
python web2md.py <URL> [--clean-transcripts]
```

Replace `<URL>` with the web page you want to convert. Options:

- `--clean-transcripts`: Optional. Attempts to clean up and format transcript-style text that may be mangled in the conversion process. This is particularly useful for podcast transcripts or interview content.

The script will:

1. Download the specified web page.
2. Convert the HTML content to Markdown.
3. Save the markdown file and images in a structured directory based on the current date and the domain of the URL.

## Output Structure

```
BASE_OUTPUT_DIR/
└── YYYY-MM-DD/
    └── domain.tld/
        └── index.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

- Ensure the URL provided is correct and try to visit it in a browser first to check for any issues.
- Make sure you have the permissions to write in the output directory specified.

