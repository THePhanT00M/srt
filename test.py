import whisperx
import os
from pyannote.audio import Pipeline

def transcribe_with_whisperx(audio_path, model='small'):
    # Load WhisperX model
    model = whisperx.load_model(model, 'cpu', compute_type='int8')
    # Transcribe audio
    result = model.transcribe(audio_path)
    return result

def diarize_audio(audio_path, pipeline):
    # Perform speaker diarization
    diarization_result = pipeline({'uri': 'audio', 'audio': audio_path})
    return diarization_result

def align_diarization_and_transcription(transcription, diarization_result):
    # Align transcription with diarization results
    aligned_subtitles = []
    for segment in diarization_result:
        start_time = segment.start
        end_time = segment.end
        speaker = segment.speaker

        for trans in transcription['segments']:
            trans_start = trans['start']
            trans_end = trans['end']
            text = trans['text']

            if trans_start >= start_time and trans_end <= end_time:
                aligned_subtitles.append({
                    'start': trans_start,
                    'end': trans_end,
                    'speaker': speaker,
                    'text': text
                })
    return aligned_subtitles

def save_subtitles_to_srt(subtitles, output_path):
    # Save subtitles to SRT file
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, subtitle in enumerate(subtitles):
            f.write(f"{i+1}\n")
            f.write(f"{format_timestamp(subtitle['start'])} --> {format_timestamp(subtitle['end'])}\n")
            f.write(f"Speaker {subtitle['speaker']}: {subtitle['text']}\n")
            f.write("\n")

def format_timestamp(seconds):
    # Format timestamp for SRT
    millis = int((seconds - int(seconds)) * 1000)
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def main(audio_path, output_srt_path, whisper_model='small', pyannote_token='YOUR_PYANNOTE_API_TOKEN'):
    # Load diarization pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=pyannote_token)

    # Transcribe audio with WhisperX
    transcription = transcribe_with_whisperx(audio_path, whisper_model)

    # Perform speaker diarization
    diarization_result = diarize_audio(audio_path, pipeline)

    # Align transcription with diarization results
    aligned_subtitles = align_diarization_and_transcription(transcription, diarization_result)

    # Save aligned subtitles to SRT file
    save_subtitles_to_srt(aligned_subtitles, output_srt_path)

# Example usage
audio_path = "./dataset/audio/extracted_audio.mp3"
output_srt_path = "subtitles.srt"
whisper_model = 'large-v3'
pyannote_token = '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'


if __name__ == '__main__':
    main(audio_path, output_srt_path, whisper_model, pyannote_token)