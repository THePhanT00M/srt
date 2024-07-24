import json

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def interpolate_timestamps(words, start_time, end_time):
    timestamps = []
    prev_time = start_time
    next_time = end_time
    for word in words:
        if 'start' in word and 'end' in word:
            if word['start'] is not None and word['end'] is not None:
                prev_time = word['start']
            else:
                word['start'] = prev_time

            if word['end'] is not None:
                next_time = word['end']
            else:
                word['end'] = next_time
        else:
            word['start'] = prev_time
            word['end'] = next_time

        timestamps.append(word)
    return timestamps

def should_split_line(line_words, new_word, line_duration, line_length):
    if line_duration < 0.5:
        return False
    if line_duration > 10:
        return True
    if line_length + len(new_word['word']) > 50:
        return True
    if line_length > 10 and new_word['word'] in [".", "?", "!"]:
        return True
    return False

def split_lines(words):
    lines = []
    current_line = []
    line_start_time = words[0]['start']
    line_length = 0

    for word in words:
        current_line.append(word)
        line_length += len(word['word'])
        line_end_time = word['end']
        line_duration = line_end_time - line_start_time

        if should_split_line(current_line, word, line_duration, line_length):
            lines.append(current_line)
            current_line = []
            line_start_time = word['start']
            line_length = 0

    if current_line:
        lines.append(current_line)

    return lines

def process_transcription(transcription):
    segments = []
    for segment in transcription:
        start_time = segment['start']
        end_time = segment['end']
        words = segment['words']
        interpolated_words = interpolate_timestamps(words, start_time, end_time)
        lines = split_lines(interpolated_words)
        for line in lines:
            line_text = " ".join([word['word'] for word in line])
            segments.append({
                "start": line[0]['start'],
                "end": line[-1]['end'],
                "text": line_text
            })
    return segments

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    milliseconds = int((secs - int(secs)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(secs):02}.{milliseconds:03}"

def save_to_vtt(segments, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("WEBVTT\n\n")
        for segment in segments:
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            file.write(f"{start} --> {end}\n")
            file.write(f"{segment['text']}\n\n")

# JSON 데이터를 로드하고 처리합니다
transcription = load_json('./dataset/json/youtube.json')
segments = process_transcription(transcription)
save_to_vtt(segments, 'output.vtt')