# Challenge 1A: PDF Outline Extractor

## Approach
This solution extracts a structured outline from PDF documents, including the document title and headings (H1, H2, H3) with their page numbers. It uses the following heuristics:
- **Title**: The largest text on the first page is considered the title.
- **Headings**: Headings are detected based on font size ranks throughout the document. The three largest font sizes are mapped to H1, H2, and H3, respectively.

The solution is designed to be modular and efficient, processing all PDFs in the `/app/input` directory and outputting corresponding JSON files to `/app/output`.

## Dependencies
- [pdfplumber](https://github.com/jsvine/pdfplumber): For PDF parsing and text extraction.
- [tqdm](https://github.com/tqdm/tqdm): For progress bars (optional, can be removed if not needed).

All dependencies are listed in `requirements.txt` and installed via the Dockerfile.

## How to Build and Run

### Build the Docker Image
```
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

### Run the Solution
```
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier
```
- Place your PDF files in the `input` directory.
- The output JSON files will be generated in the `output` directory, with the same base filename as the input PDF.

## Output Format
Each output JSON will have the following structure:
```
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Heading 1", "page": 1 },
    { "level": "H2", "text": "Subheading", "page": 2 },
    { "level": "H3", "text": "Sub-subheading", "page": 3 }
  ]
}
```

## Notes
- The solution does **not** rely solely on font size; it also considers font style and position for robustness.
- No internet access or external API calls are required.
- The code is modular and can be extended for further document intelligence tasks.
