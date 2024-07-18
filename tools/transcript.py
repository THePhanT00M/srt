import os
import logging
import re
import pandas as pd
from typing import List, Tuple
from tools.utils import format_time, emotion_to_text

logging.basicConfig(level=logging.ERROR)

def generate_smi(filename: str, subtitles: List[Tuple[float, float, str]], output_dir: str = "dataset/output/", lang: str = "ko"):
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



def generate_subtitles(whispers, max_line_length = 50):
    subtitles = []
    current_subtitle = ''
    current_start_time = None
    current_end_time = None

    for segment in whispers:
        for word_info in segment['words']:
            word = word_info['word']
            start_time = word_info['start']
            end_time = word_info['end']

            if current_start_time is None:
                current_start_time = start_time

            if len(current_subtitle) + len(word) + 1 <= max_line_length:
                if current_subtitle:
                    current_subtitle += ' '
                current_subtitle += word
                current_end_time = end_time
            else:
                subtitles.append((current_start_time, current_end_time, current_subtitle))
                current_subtitle = word
                current_start_time = start_time
                current_end_time = end_time

    if current_subtitle:
        subtitles.append((current_start_time, current_end_time, current_subtitle))

    return subtitles