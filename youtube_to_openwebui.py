#!/usr/bin/env python3
"""
YouTube Transcript Extractor

This script takes a list of YouTube video URLs, extracts their transcriptions,
and saves them to local files for later use with OpenWebUI.
"""

import os
import sys
import argparse
import json
import hashlib
import re
from typing import List, Dict, Any, Optional
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class YouTubeTranscriptionExtractor:
    """Class to extract transcriptions from YouTube videos."""
    
    def __init__(self):
        self.formatter = TextFormatter()
    
    def extract_video_id(self, url: str) -> str:
        """Extract the video ID from a YouTube URL."""
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        elif "youtube.com/watch" in url:
            import urllib.parse as urlparse
            parsed_url = urlparse.urlparse(url)
            return urlparse.parse_qs(parsed_url.query)['v'][0]
        else:
            raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get video title and channel name using YouTube's oEmbed API."""
        try:
            # Use YouTube's oEmbed API to get video information
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract title and author (channel name)
            title = data.get('title', f"YouTube Video {video_id}")
            author = data.get('author_name', "YouTube Creator")
            
            return {"title": title, "author": author}
        except Exception as e:
            print(f"Error fetching video info for {video_id}: {e}")
            # Fallback to default values
            return {"title": f"YouTube Video {video_id}", "author": "YouTube Creator"}
    
    def get_transcript(self, url: str) -> Optional[str]:
        """Get the transcript for a YouTube video."""
        try:
            video_id = self.extract_video_id(url)
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            formatted_transcript = self.formatter.format_transcript(transcript)
            return formatted_transcript
        except Exception as e:
            print(f"Error extracting transcript for {url}: {e}")
            return None


class TranscriptFileManager:
    """Class to manage transcript files."""
    
    def __init__(self, output_dir: str):
        """Initialize with the output directory."""
        self.output_dir = output_dir
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        # Keep track of processed video IDs to avoid duplicates in a single run
        self.processed_ids = set()
    
    def sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in a filename."""
        # Replace invalid filename characters with underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', text)
        # Limit length to avoid excessively long filenames
        return sanitized[:100] if len(sanitized) > 100 else sanitized
    
    def generate_filename(self, video_id: str, title: str = None, author: str = None) -> str:
        """Generate a unique filename for a video using its ID, author, and title."""
        # Ensure the video ID is valid for a filename
        safe_id = ''.join(c for c in video_id if c.isalnum() or c in '-_')
        
        if author and title:
            # Sanitize the author name
            safe_author = self.sanitize_filename(author)
            
            # Get up to five words from the title
            title_words = title.split()[:5]
            short_title = ' '.join(title_words)
            safe_title = self.sanitize_filename(short_title)
            
            return f"{safe_id}_{safe_author}_{safe_title}.md"
        else:
            return f"{safe_id}.md"
    
    def file_exists(self, video_id: str) -> bool:
        """Check if a file already exists for this video ID, regardless of title."""
        # Look for any file that starts with the video ID
        pattern = f"{video_id}_*.md"
        simple_pattern = f"{video_id}.md"
        
        # Check for files with the pattern video_id_*.md or just video_id.md
        for filename in os.listdir(self.output_dir):
            if filename.startswith(f"{video_id}_") or filename == simple_pattern:
                return True
        
        return False
    
    def is_duplicate(self, video_id: str) -> bool:
        """Check if this video ID has already been processed in this run."""
        return video_id in self.processed_ids
    
    def save_transcript(self, video_id: str, url: str, video_info: Dict[str, Any], transcript: str) -> str:
        """Save a transcript to a file."""
        # Mark this video ID as processed
        self.processed_ids.add(video_id)
        
        # Generate filename from video ID, title, and author
        filename = self.generate_filename(video_id, video_info['title'], video_info['author'])
        file_path = os.path.join(self.output_dir, filename)
        
        # Format the content with title, author, URL, and transcript
        content = f"# {video_info['title']}\n"
        content += f"Author: {video_info['author']}\n\n"
        content += f"URL: {url}\n\n"
        content += transcript
        
        # Write the content to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path


def process_urls_from_file(file_path: str) -> List[str]:
    """Read URLs from a file, one URL per line."""
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    return urls


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Extract YouTube video transcriptions and save them to files.')
    parser.add_argument('--urls', type=str, help='Comma-separated list of YouTube URLs')
    parser.add_argument('--file', type=str, help='File containing YouTube URLs (one per line)')
    parser.add_argument('--output-dir', type=str, default='transcripts', help='Directory to save transcript files')
    parser.add_argument('--skip-existing', action='store_true', help='Skip videos that already have transcript files')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing transcript files')
    
    args = parser.parse_args()
    
    # Get URLs from arguments or file
    urls = []
    if args.urls:
        urls = [url.strip() for url in args.urls.split(',')]
    elif args.file:
        urls = process_urls_from_file(args.file)
    else:
        print("Error: No URLs provided. Use --urls or --file argument.")
        sys.exit(1)
    
    if not urls:
        print("No valid URLs found.")
        sys.exit(1)
    
    # Initialize the transcript extractor and file manager
    extractor = YouTubeTranscriptionExtractor()
    file_manager = TranscriptFileManager(args.output_dir)
    
    # Process each URL
    success_count = 0
    skipped_count = 0
    duplicate_count = 0
    
    for url in urls:
        try:
            print(f"Processing: {url}")
            video_id = extractor.extract_video_id(url)
            
            # Check if this video ID has already been processed in this run
            if file_manager.is_duplicate(video_id):
                print(f"Skipping: Duplicate URL for video ID {video_id}")
                duplicate_count += 1
                continue
            
            # Check if the file already exists
            if file_manager.file_exists(video_id) and not args.overwrite:
                if args.skip_existing:
                    print(f"Skipping: Transcript for video ID {video_id} already exists")
                    skipped_count += 1
                    continue
                else:
                    print(f"Warning: Transcript for video ID {video_id} already exists. Use --overwrite to replace it.")
            
            # Get the transcript
            transcript = extractor.get_transcript(url)
            
            if transcript:
                # Get video info
                video_info = extractor.get_video_info(video_id)
                
                # Save the transcript to a file
                file_path = file_manager.save_transcript(video_id, url, video_info, transcript)
                
                print(f"Saved transcript to: {file_path}")
                success_count += 1
        except Exception as e:
            print(f"Error processing {url}: {e}")
    
    print(f"Completed: {success_count} videos processed successfully, {skipped_count} skipped, {duplicate_count} duplicates.")
    print(f"Transcripts saved to: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main() 