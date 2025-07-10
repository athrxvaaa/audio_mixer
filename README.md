# BGM Inserter

A Python script that automatically analyzes video and audio content, transcribes audio using OpenAI's Whisper API, and inserts suitable background music based on the content's theme using GPT-4o Mini for analysis.

## Features

- 🎬 **Video Processing**: Extract audio from video files and add dynamic BGM
- 🎵 **Audio Processing**: Convert audio files to videos with adaptive BGM
- 🎤 **Advanced Transcription**: Use OpenAI Whisper API with detailed segments
- 🧠 **Dynamic Theme Analysis**: Analyze content segments using GPT-4o Mini
- 🎵 **Adaptive BGM**: Background music that changes based on content themes
- 🔊 **Smart Audio Mixing**: Blend original audio with dynamic background music
- 🎯 **Customizable**: Adjust BGM volume, resolution, and output settings
- 📁 **Batch Processing**: Process multiple files at once
- 🎭 **Segment-Based Music**: Different BGM styles for different content segments

## Requirements

- Python 3.8+
- OpenAI API key
- Jamendo API key (optional, for real music)
- FFmpeg (for video processing)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (if not already installed):

   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

4. **Set up your API keys**:
   - Create a `.env` file in the project directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_actual_api_key_here`
   - Add your Jamendo API key (optional): `JAMENDO_API_KEY=your_jamendo_api_key_here`
   - Get your OpenAI API key from: https://platform.openai.com/api-keys
   - Get your Jamendo API key from: https://developer.jamendo.com/

## Usage

### Basic Usage

```bash
# Process a video file
python bgm_inserter.py path/to/your/video.mp4

# Process an audio file
python bgm_inserter.py path/to/your/audio.mp3
```

### Advanced Usage

```bash
# Specify output file
python bgm_inserter.py input_video.mp4 -o output_video.mp4
python bgm_inserter.py input_audio.mp3 -o output_video.mp4

# Adjust BGM volume (0.0 to 1.0)
python bgm_inserter.py input_file.mp4 --bgm-volume 0.5

# Set video resolution for audio files
python bgm_inserter.py input_audio.mp3 --resolution 1280 720
```

### Command Line Arguments

- `input_path`: Path to the input video or audio file (required)
- `-o, --output`: Path for the output video file (optional)
- `--bgm-volume`: Volume level for background music, 0.0 to 1.0 (default: 0.3)
- `--resolution`: Video resolution for audio files, width height (default: 1920 1080)

## How It Works

### For Video Files:

1. **Audio Extraction**: Extracts audio from the input video file
2. **Advanced Transcription**: Uses OpenAI Whisper API with detailed segments and timestamps
3. **Dynamic Theme Analysis**: Analyzes each segment separately using GPT-4o Mini
4. **Adaptive BGM Creation**: Generates different music styles for different content segments
5. **Smart Audio Mixing**: Combines original audio with dynamic background music
6. **Video Output**: Creates the final video with adaptive background music

### For Audio Files:

1. **Audio Preparation**: Converts audio to WAV format if needed
2. **Advanced Transcription**: Uses OpenAI Whisper API with detailed segments and timestamps
3. **Dynamic Theme Analysis**: Analyzes each segment separately using GPT-4o Mini
4. **Adaptive BGM Creation**: Generates different music styles for different content segments
5. **Video Creation**: Creates a video with gradient background and dynamic audio
6. **Video Output**: Saves the final video with adaptive background music

## Example Output

```
Starting BGM insertion process for: sample_video.mp4
Extracting audio from video...
Audio extracted to: /tmp/tmp12345.wav
Transcribing audio with Whisper API (detailed mode)...
Detailed transcription completed successfully!
Transcription: Hello everyone, welcome to our tutorial on machine learning...
Analyzing video theme with GPT-4o Mini (detailed segments)...
Dynamic theme analysis completed!
Overall Theme: educational, Mood: informative
Dynamic Segments: 5
Searching for suitable background music...
Creating dynamic BGM with adaptive segments...
  Segment 1: ambient (0.0s - 15.2s)
  Segment 2: energetic (15.2s - 32.8s)
  Segment 3: dramatic (32.8s - 45.1s)
  Segment 4: ambient (45.1s - 58.3s)
  Segment 5: energetic (58.3s - 72.0s)
Dynamic BGM created: /tmp/tmp67890.wav
Inserting background music into video...
Video with BGM saved to: sample_video_with_bgm.mp4
BGM insertion process completed successfully!

✅ Success! Video with adaptive BGM saved to: sample_video_with_bgm.mp4
```

## Supported Formats

### Video Formats:

- MP4
- AVI
- MOV
- MKV
- WebM
- FLV
- WMV
- M4V

### Audio Formats:

- MP3
- WAV
- M4A
- AAC
- FLAC
- OGG
- WMA

_All formats supported by FFmpeg_

## API Usage

The script uses:

- **Whisper API**: For audio transcription
- **GPT-4o Mini**: For theme analysis and BGM recommendations

### Cost Estimation

- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4o Mini**: ~$0.00015 per 1K tokens (analysis typically uses 200-500 tokens)

For a 10-minute video, estimated cost: ~$0.06-0.08

## Customization

### Music Integration

The script now supports real music from Jamendo API:

1. **Jamendo Music API**: Free music with API access (integrated)
   - 600,000+ tracks available
   - Search by genre, mood, and keywords
   - 200 requests/day on free tier
   - Automatic fallback to generated BGM if no suitable tracks found

2. **Generated BGM**: Synthesized background music (fallback)
   - Created when Jamendo API is not available
   - Customizable styles and instruments
   - Dynamic segments with smooth transitions

3. **Other Options**: Additional music services can be integrated:
   - Free Music Archive: Large collection of free music
   - YouTube Audio Library: Free music for content creators
   - Premium Services: Spotify, Apple Music APIs (require licensing)

### Theme Analysis Customization

Modify the `analyze_video_theme` method to adjust:

- Analysis prompts
- Response structure
- Theme categories
- Music recommendations

## Troubleshooting

### Common Issues

1. **"FFmpeg not found"**:

   - Install FFmpeg and ensure it's in your system PATH

2. **"OPENAI_API_KEY not set"**:

   - Create a `.env` file with your API key
   - Or set the environment variable: `export OPENAI_API_KEY=your_key`

3. **"Video file not found"**:

   - Check the file path and ensure the video file exists

4. **Memory issues with large videos**:
   - Process videos in smaller chunks
   - Ensure sufficient RAM (recommended: 8GB+)

### Performance Tips

- Use SSD storage for faster processing
- Close other applications during processing
- For large videos, consider processing during off-peak hours

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Areas for improvement:

- Integration with music APIs
- Enhanced theme analysis
- Batch processing capabilities
- GUI interface
- More sophisticated BGM generation

## Disclaimer

- Ensure you have rights to use any background music
- Respect copyright and licensing requirements
- Test with sample videos before processing important content
