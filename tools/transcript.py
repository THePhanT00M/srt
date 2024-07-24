import os
import logging
from typing import List, Tuple
from tools.utils import format_time, emotion_to_text

logging.basicConfig(level=logging.ERROR)

def generate_smi(filename: str, subtitles: List[Tuple[float, float, str]], output_dir: str = "./dataset/output/", lang: str = "ko"):
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as f:
        f.write("<SAMI>\n")
        f.write("<HEAD>\n")
        f.write("<Title>Sample SMI file</Title>\n")
        f.write("</HEAD>\n")
        f.write("<BODY>\n")
        for start_time, _, text in subtitles:
            f.write(f"<SYNC Start={int(start_time * 1000)}>\n")
            f.write(f"<P Class={lang}CC>{text}</P>\n")
            f.write("</SYNC>\n")
        f.write("</BODY>\n")
        f.write("</SAMI>\n")

def generate_srt(filename: str, subtitles: List[Tuple[float, float, str]], output_dir: str = "dataset/output/"):
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as f:
        subtitle_number = 1
        for start_time, end_time, text in subtitles:
            f.write(f"{subtitle_number}\n")
            f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            f.write(f"{text}\n\n")
            subtitle_number += 1

def generate_txt(filename: str, subtitles: List[Tuple[float, float, str]], output_dir: str = "dataset/output/"):
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as f:
        for _, _, text in subtitles:
            f.write(f"{text}\n")


def matching_formats(subtitles, args):
    if args.output_type == 'all':
        generate_smi(args.output_path, subtitles)
        generate_srt(args.output_path, subtitles)
        generate_txt(args.output_path, subtitles)
    elif args.output_type == 'smi':
        return generate_smi(args.output_path, subtitles)
    elif args.output_type == 'srt':
        return generate_srt(args.output_path, subtitles)
    elif args.output_type == 'txt':
        return generate_txt(args.output_path, subtitles)
    else:
        raise ValueError(f"Invalid output type: {args.output_type}")



def generate_subtitles(tags_df, whispers, speech_moods = ''):
    subtitles = []
    for index, row in tags_df.iterrows():
        start_time = row['start_time']
        end_time = row['end_time']
        tag_name = row['name']

        # Generate Speaker's text
        whisper_text = ''
        for segment in whispers['segments']:
            if segment['start'] <= start_time and segment['end'] >= end_time:
                whisper_text = segment['text']
                break

        '''
        # Generate speaker's emotion text
        mood_text = ''
        if 'speech' in tag_name:
            mood_text = emotion_to_text(speech_moods['emotion'])
        '''

        # if you want to try background sound mood detection, uncomment this code
        '''
        if 'sound' in tag_name:
            mood_text = predict_sound_mood(tag_name)
        '''

        subtitle_text = f"{whisper_text}"
        subtitles.append((start_time, end_time, subtitle_text))

    return subtitles
