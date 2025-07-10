import os
import json
import tempfile
from pathlib import Path
from typing import Optional
from pydub import AudioSegment
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class BGMInserter:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.whisper_model = "whisper-1"
        self.gpt_model = "gpt-4o-mini"
        self.audio_folder = "audio"
        self.bgm_files = []
        for f in os.listdir(self.audio_folder):
            if f.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma')):
                file_path = str(Path(self.audio_folder) / f)
                try:
                    if os.path.getsize(file_path) == 0:
                        print(f"Warning: Skipping empty audio file: {file_path}")
                        continue
                    _ = AudioSegment.from_file(file_path)
                    self.bgm_files.append(file_path)
                except Exception as e:
                    print(f"Warning: Skipping invalid audio file: {file_path} ({e})")
        if not self.bgm_files:
            raise RuntimeError("No valid BGM audio files found in the 'audio' folder.")

    def prepare_audio_file(self, audio_path: str) -> str:
        if audio_path.lower().endswith('.wav'):
            return audio_path
        audio = AudioSegment.from_file(audio_path)
        temp_audio_path = tempfile.mktemp(suffix='.wav')
        audio.export(temp_audio_path, format='wav')
        return temp_audio_path

    def transcribe_audio_with_whisper(self, audio_path: str) -> dict:
        print("Transcribing audio with Whisper API (detailed mode)...")
        with open(audio_path, 'rb') as audio_file:
            transcript = self.openai_client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        if hasattr(transcript, "model_dump"):
            transcription_data = transcript.model_dump()
        else:
            transcription_data = dict(transcript)
        return transcription_data

    def group_segments_by_topic(self, segments):
        # Prepare a prompt for GPT to group segments by topic/tone
        prompt = """
You are an expert at analyzing transcripts for topic and tone changes. Given a list of segments with start/end times and text, group consecutive segments that share the same topic or tone. Return a JSON array of groups, each with:
- start: start time in seconds
- end: end time in seconds
- description: short description of the topic/tone

Example output:
[
  {"start": 0, "end": 30, "description": "Introduction and welcome"},
  {"start": 30, "end": 90, "description": "Explaining the main concept"},
  {"start": 90, "end": 120, "description": "Q&A and closing remarks"}
]

Segments:
"""
        for seg in segments:
            prompt += f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text'].strip()}\n"
        prompt += "\nReturn only the JSON array."
        response = self.openai_client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {"role": "system", "content": "You are a transcript analysis expert. Always return valid JSON."},
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
        print("\nDetected topic/tone groups:")
        for g in groups:
            print(f"  {g['start']:.1f}s - {g['end']:.1f}s: {g['description']}")
        return groups

    def process_audio(self, audio_path: str, output_path: Optional[str] = None) -> str:
        print(f"Processing audio file: {audio_path}")
        prepared_audio_path = self.prepare_audio_file(audio_path)
        transcription_data = self.transcribe_audio_with_whisper(prepared_audio_path)
        segments = transcription_data.get('segments', [])
        orig_audio = AudioSegment.from_file(prepared_audio_path)
        total_duration = orig_audio.duration_seconds
        print(f"Total duration: {total_duration:.2f}s, Segments: {len(segments)}")
        # Group segments by topic/tone using GPT
        groups = self.group_segments_by_topic(segments)
        # Prepare BGM for each group
        bgm_segments = []
        for i, group in enumerate(groups):
            start = int(group['start'] * 1000)
            end = int(group['end'] * 1000)
            bgm_file = self.bgm_files[i % len(self.bgm_files)]
            bgm = AudioSegment.from_file(bgm_file)
            seg_len = end - start
            if len(bgm) < seg_len:
                loops_needed = int(seg_len / len(bgm)) + 1
                bgm = bgm * loops_needed
            bgm = bgm[:seg_len]
            # Crossfade with previous/next BGM for smooth transitions
            fade_ms = min(2000, seg_len // 4)
            bgm = bgm.fade_in(fade_ms).fade_out(fade_ms)
            bgm_segments.append((start, end, bgm))
        # Create full BGM track
        full_bgm = AudioSegment.silent(duration=len(orig_audio))
        for start, end, bgm in bgm_segments:
            # Reduce only the BGM volume by 70%, keep original audio unchanged
            bgm = bgm - 8.5  # ~30% perceived loudness
            full_bgm = full_bgm.overlay(bgm, position=start)
        # Mix original audio (unchanged) with reduced-volume BGM
        mixed = orig_audio.overlay(full_bgm)
        if not output_path:
            output_path = str(Path("output_audio") / (Path(audio_path).stem + "_with_bgm.wav"))
        Path("output_audio").mkdir(exist_ok=True)
        mixed.export(output_path, format='wav')
        print(f"Processed audio with topic/tone-aware BGM saved to: {output_path}")
        return output_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Insert topic/tone-aware BGM into audio based on GPT analysis')
    parser.add_argument('input_path', help='Path to the input audio file')
    parser.add_argument('-o', '--output', help='Path for the output audio file')
    args = parser.parse_args()
    inserter = BGMInserter()
    inserter.process_audio(args.input_path, args.output)

if __name__ == "__main__":
    main() 