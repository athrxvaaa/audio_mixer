#!/usr/bin/env python3
"""
Batch processing script for BGM Inserter.
Processes all videos in the input_videos folder.
"""

import os
import sys
from pathlib import Path
from typing import List
import argparse

from bgm_inserter import BGMInserter

def get_media_files(input_dir: str) -> List[str]:
    """
    Get all video and audio files from the input directory.
    
    Args:
        input_dir: Path to input directory
        
    Returns:
        List of media file paths
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
    media_extensions = video_extensions | audio_extensions
    
    media_files = []
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return []
    
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in media_extensions:
            media_files.append(str(file_path))
    
    return sorted(media_files)

def process_media_batch(input_dir: str = "input_videos", 
                       output_dir: str = "output_videos",
                       bgm_volume: float = 0.3,
                       skip_existing: bool = True,
                       resolution: tuple = (1920, 1080)):
    """
    Process all videos and audio files in the input directory.
    
    Args:
        input_dir: Directory containing input media files
        output_dir: Directory for output videos
        bgm_volume: Volume level for background music
        skip_existing: Skip processing if output file already exists
        resolution: Video resolution for audio files
    """
    print(f"🎬 Batch Processing Media Files")
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🔊 BGM Volume: {bgm_volume}")
    print(f"📐 Resolution: {resolution[0]}x{resolution[1]}")
    print("=" * 60)
    
    # Get media files
    media_files = get_media_files(input_dir)
    
    if not media_files:
        print(f"❌ No media files found in {input_dir}")
        print(f"Supported video formats: .mp4, .avi, .mov, .mkv, .webm, .flv, .wmv, .m4v")
        print(f"Supported audio formats: .mp3, .wav, .m4a, .aac, .flac, .ogg, .wma")
        return
    
    print(f"📹 Found {len(media_files)} media file(s) to process:")
    for i, media_file in enumerate(media_files, 1):
        file_path = Path(media_file)
        file_type = "🎵 Audio" if file_path.suffix.lower() in {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'} else "🎬 Video"
        print(f"  {i}. {file_path.name} ({file_type})")
    print()
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Initialize BGM inserter
    inserter = BGMInserter()
    
    # Process each media file
    successful = 0
    failed = 0
    
    for i, media_file in enumerate(media_files, 1):
        media_name = Path(media_file).name
        media_stem = Path(media_file).stem
        media_ext = Path(media_file).suffix.lower()
        
        # Determine if it's audio or video
        audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
        is_audio = media_ext in audio_extensions
        
        # Generate output filename
        if is_audio:
            output_file = output_path / f"{media_stem}_video.mp4"
        else:
            output_file = output_path / f"{media_stem}_with_bgm{media_ext}"
        
        print(f"🎬 Processing {i}/{len(media_files)}: {media_name}")
        
        # Check if output already exists
        if skip_existing and output_file.exists():
            print(f"⏭️  Skipping (output already exists): {output_file.name}")
            successful += 1
            continue
        
        try:
            # Process the media file
            if is_audio:
                result_path = inserter.process_audio(media_file, str(output_file), resolution)
            else:
                result_path = inserter.process_video(media_file, str(output_file))
            
            if os.path.exists(result_path):
                print(f"✅ Success: {output_file.name}")
                successful += 1
            else:
                print(f"❌ Failed: Output file not created")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error processing {media_name}: {e}")
            failed += 1
        
        print("-" * 40)
    
    # Summary
    print("=" * 60)
    print(f"📊 Batch Processing Complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output files saved to: {output_dir}")
    
    if successful > 0:
        print(f"\n🎉 {successful} media file(s) processed successfully!")
    if failed > 0:
        print(f"⚠️  {failed} media file(s) failed to process.")

def main():
    """Main function for batch processing."""
    parser = argparse.ArgumentParser(description='Batch process videos and audio files with BGM insertion')
    parser.add_argument('--input-dir', default='input_videos', 
                       help='Input directory containing media files (default: input_videos)')
    parser.add_argument('--output-dir', default='output_videos',
                       help='Output directory for processed videos (default: output_videos)')
    parser.add_argument('--bgm-volume', type=float, default=0.3,
                       help='BGM volume level (0.0 to 1.0, default: 0.3)')
    parser.add_argument('--resolution', nargs=2, type=int, default=[1920, 1080],
                       help='Video resolution for audio files (width height, default: 1920 1080)')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing even if output files exist')
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key in a .env file or environment variable.")
        return 1
    
    try:
        process_media_batch(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            bgm_volume=args.bgm_volume,
            skip_existing=not args.force,
            resolution=tuple(args.resolution)
        )
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Batch processing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 