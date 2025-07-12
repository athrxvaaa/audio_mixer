import os
import json
import tempfile
from pathlib import Path
from typing import Optional, List
from pydub import AudioSegment
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class BGMInserterService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.whisper_model = "whisper-1"
        self.gpt_model = "gpt-4o-mini"
        self.themed_bgm_files = {}
        self._load_bgm_files_local()

    def _load_bgm_files_local(self):
        """Load BGM files from local folder only."""
        audio_folder = "BGM"
        if not os.path.exists(audio_folder):
            raise RuntimeError(f"BGM folder '{audio_folder}' not found.")
        
        # Map folder names to theme names
        folder_to_theme_mapping = {
            'Start HOOK': 'Hook',
            'WHAT': 'What',
            'WHY ': 'Why',  # Note: folder has trailing space
            'HOW': 'How',
            'End HOOK': 'Ending Hook'
        }
        
        for folder_name, theme in folder_to_theme_mapping.items():
            theme_folder_path = Path(audio_folder) / folder_name
            if theme_folder_path.exists() and theme_folder_path.is_dir():
                # Get all audio files in the theme folder
                audio_files = []
                for file_path in theme_folder_path.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ('.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'):
                        try:
                            if file_path.stat().st_size == 0:
                                print(f"Warning: Skipping empty audio file: {file_path}")
                                continue
                            _ = AudioSegment.from_file(str(file_path))
                            audio_files.append(str(file_path))
                            print(f"Loaded theme '{theme}' file: {file_path.name}")
                        except Exception as e:
                            print(f"Warning: Skipping invalid audio file: {file_path} ({e})")
                
                if audio_files:
                    self.themed_bgm_files[theme] = audio_files
                    print(f"Loaded {len(audio_files)} files for theme '{theme}' from local folder")
                else:
                    print(f"Warning: No valid audio files found in theme folder: {folder_name}")
            else:
                print(f"Warning: Theme folder not found: {folder_name}")
        
        if not self.themed_bgm_files:
            raise RuntimeError("No valid themed BGM audio files found in the BGM folder structure.")

    def get_available_bgm_files(self) -> List[str]:
        """Get a list of available themed BGM file names."""
        result = []
        for theme, file_paths in self.themed_bgm_files.items():
            for file_path in file_paths:
                result.append(f"{theme}: {Path(file_path).name}")
        return result

    def prepare_audio_file(self, audio_path: str) -> str:
        """Convert audio file to WAV format if needed."""
        if audio_path.lower().endswith('.wav'):
            return audio_path
        audio = AudioSegment.from_file(audio_path)
        temp_audio_path = tempfile.mktemp(suffix='.wav')
        audio.export(temp_audio_path, format='wav')
        return temp_audio_path

    def transcribe_audio_with_whisper(self, audio_path: str) -> dict:
        """Transcribe audio using OpenAI Whisper API."""
        print("Transcribing audio with Whisper API (detailed mode)...")
        with open(audio_path, 'rb') as audio_file:
            transcript = self.openai_client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file,
                response_format="verbose_json"
            )
        if hasattr(transcript, "model_dump"):
            transcription_data = transcript.model_dump()
        else:
            transcription_data = dict(transcript)
        return transcription_data

    def group_segments_by_topic(self, segments):
        """Group transcript segments by 5 specific themes: Hook, What, Why, How, Ending Hook."""
        prompt = """
You are an expert at analyzing transcripts and categorizing content into 5 specific themes. Given a list of segments with start/end times and text, group consecutive segments into these 5 categories:

1. **Hook** - Introduction, attention-grabbing content, opening statements
2. **What** - Definition, explanation of what something is, description of concepts
3. **Why** - Reasons, motivations, benefits, importance, purpose
4. **How** - Methods, processes, steps, implementation, practical application
5. **Ending Hook** - Conclusion, call-to-action, final thoughts, closing statements

Return a JSON array of groups, each with:
- start: start time in seconds
- end: end time in seconds
- theme: one of "Hook", "What", "Why", "How", "Ending Hook"

Example output:
[
  {"start": 0, "end": 30, "theme": "Hook"},
  {"start": 30, "end": 90, "theme": "What"},
  {"start": 90, "end": 150, "theme": "Why"},
  {"start": 150, "end": 200, "theme": "How"},
  {"start": 200, "end": 220, "theme": "Ending Hook"}
]

Segments:
"""
        for seg in segments:
            prompt += f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text'].strip()}\n"
        prompt += "\nReturn only the JSON array with the 5 themes."
        
        response = self.openai_client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {"role": "system", "content": "You are a transcript analysis expert. Always return valid JSON with exactly 5 theme categories: Hook, What, Why, How, Ending Hook."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        
        text = response.choices[0].message.content.strip()
        # Extract JSON
        if text.startswith('```json'):
            text = text.split('```json')[1].split('```')[0]
        elif text.startswith('```'):
            text = text.split('```')[1]
        
        groups = json.loads(text)
        print("\nDetected theme groups:")
        for g in groups:
            print(f"  {g['start']:.1f}s - {g['end']:.1f}s: {g['theme']}")
        return groups

    def process_audio(self, audio_path: str, output_path: Optional[str] = None, bgm_volume_reduction: float = 35.0) -> str:
        """Process audio file by adding background music based on content analysis."""
        print(f"Processing audio file: {audio_path}")
        
        # Prepare audio file
        prepared_audio_path = self.prepare_audio_file(audio_path)
        
        # Transcribe audio
        transcription_data = self.transcribe_audio_with_whisper(prepared_audio_path)
        segments = transcription_data.get('segments', [])
        
        # Load original audio
        orig_audio = AudioSegment.from_file(prepared_audio_path)
        total_duration = orig_audio.duration_seconds
        print(f"Total duration: {total_duration:.2f}s, Segments: {len(segments)}")
        
        # Group segments by topic/tone using GPT
        groups = self.group_segments_by_topic(segments)
        
        # Prepare BGM for each group based on themes
        bgm_segments = []
        import random
        
        for group in groups:
            start = int(group['start'] * 1000)
            end = int(group['end'] * 1000)
            theme = group['theme']
            
            # Get the corresponding themed BGM files
            if theme in self.themed_bgm_files:
                # Randomly select one of the available BGM files for this theme
                bgm_files = self.themed_bgm_files[theme]
                bgm_file = random.choice(bgm_files)
                bgm = AudioSegment.from_file(bgm_file)
                seg_len = end - start
                if len(bgm) < seg_len:
                    loops_needed = int(seg_len / len(bgm)) + 1
                    bgm = bgm * loops_needed
                bgm = bgm[:seg_len]
                # Crossfade with previous/next BGM for smooth transitions
                fade_ms = min(2000, seg_len // 4)
                bgm = bgm.fade_in(fade_ms).fade_out(fade_ms)
                bgm_segments.append((start, end, bgm, theme))  # Include theme in tuple
                print(f"  Using '{theme}' BGM ({Path(bgm_file).name}) for segment {group['start']:.1f}s - {group['end']:.1f}s")
            else:
                print(f"  Warning: No BGM files found for theme '{theme}'")
                # Create silent segment if no matching theme
                seg_len = end - start
                bgm = AudioSegment.silent(duration=seg_len)
                bgm_segments.append((start, end, bgm, theme))  # Include theme in tuple
        
        # Create full BGM track
        full_bgm = AudioSegment.silent(duration=len(orig_audio))
        
        for start, end, bgm, theme in bgm_segments:
            # Apply uniform volume reduction based on parameter
            bgm = bgm - bgm_volume_reduction
            print(f"  Applied {bgm_volume_reduction}dB reduction for '{theme}' theme")
            
            full_bgm = full_bgm.overlay(bgm, position=start)
        
        # Mix original audio (unchanged) with reduced-volume BGM
        mixed = orig_audio.overlay(full_bgm)
        
        # Set output path - use a unique temporary file for API responses
        if not output_path:
            import tempfile
            output_path = tempfile.mktemp(suffix='.wav')
        
        # Ensure output directory exists if it's not a temp file
        if not output_path.startswith('/tmp') and not output_path.startswith('/var/folders'):
            Path(output_path).parent.mkdir(exist_ok=True)
        
        # Export processed audio
        mixed.export(output_path, format='wav')
        print(f"Processed audio with topic/tone-aware BGM saved to: {output_path}")
        
        return output_path 