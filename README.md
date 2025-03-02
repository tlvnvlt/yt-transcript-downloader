# YouTube Transcript Extractor

This Python script extracts transcriptions from YouTube videos and saves them to local files for later use with OpenWebUI or other knowledge bases.

## Features

- Extract transcriptions from YouTube videos
- Automatically fetch video titles and author names using YouTube's oEmbed API
- Save transcriptions to local files with proper formatting
- Process multiple YouTube URLs at once
- Support for both direct URL input and file-based input
- Skip videos that already have transcript files
- Detect and handle duplicate URLs in a single run
- Option to overwrite existing transcript files
- Intelligent filename generation using video ID, author, and title

## Requirements

- Python 3.6+
- `youtube-transcript-api` for extracting YouTube transcriptions
- `requests` for making API calls
- `python-dotenv` for loading environment variables

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-transcript-extractor.git
   cd youtube-transcript-extractor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Using Command Line Arguments

Process a comma-separated list of YouTube URLs:

```bash
python youtube_to_openwebui.py --urls "https://www.youtube.com/watch?v=dQw4w9WgXcQ,https://youtu.be/jNQXAC9IVRw"
```

Process URLs from a file (one URL per line):

```bash
python youtube_to_openwebui.py --file youtube_urls.txt
```

Specify a custom output directory:

```bash
python youtube_to_openwebui.py --file youtube_urls.txt --output-dir my_transcripts
```

Skip videos that already have transcript files:

```bash
python youtube_to_openwebui.py --file youtube_urls.txt --skip-existing
```

Overwrite existing transcript files:

```bash
python youtube_to_openwebui.py --file youtube_urls.txt --overwrite
```

## File Format for YouTube URLs

Create a text file with one YouTube URL per line. Lines starting with `#` are treated as comments and ignored:

```
# My favorite YouTube videos
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/jNQXAC9IVRw
```

## Output Format

The script saves each transcript to a separate Markdown file in the specified output directory (default: `transcripts/`). Each file is named using a combination of:
- YouTube video ID
- Channel name (author)
- First few words of the video title

For example: `dQw4w9WgXcQ_Rick_Astley_Never_Gonna_Give_You.md`

The content of each file follows this format:

```markdown
# [VIDEO_TITLE]
Author: [CHANNEL_NAME]

URL: [YOUTUBE_URL]

[TRANSCRIPT_CONTENT]
```

## Duplicate Handling

The script handles duplicates in several ways:

1. **Same Video ID in a Single Run**: If the same YouTube video appears multiple times in your input (either in the URL list or file), it will only be processed once.

2. **Existing Files from Previous Runs**: 
   - By default, the script will warn you if a transcript file already exists but will still process it.
   - Use `--skip-existing` to skip videos that already have transcript files.
   - Use `--overwrite` to replace existing transcript files with new ones.

## Using with OpenWebUI

After extracting the transcripts, you can manually upload the generated Markdown files to your OpenWebUI knowledge base through the web interface.

## Limitations

- Some videos may not have transcriptions available
- The script relies on YouTube's oEmbed API for video metadata, which may be rate-limited
- Only supports languages available in the YouTube transcript API

## License

MIT 