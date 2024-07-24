import json

# JSON 파일 불러오기
with open('json_example.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# WebVTT 파일로 저장
with open('output.vtt', 'w', encoding='utf-8') as vtt_file:
    vtt_file.write("WEBVTT\n\n")

    for entry in data:
        start = entry['start']
        end = entry['end']
        text = entry['text']
        speaker = entry['speaker']

        # 시간 형식 변환
        start_time = "{:02}:{:02}.{:03}".format(int(start // 60), int(start % 60), int((start * 1000) % 1000))
        end_time = "{:02}:{:02}.{:03}".format(int(end // 60), int(end % 60), int((end * 1000) % 1000))

        vtt_file.write(f"{start_time} --> {end_time}\n")
        vtt_file.write(f"{speaker}: {text}\n\n")

print("VTT 파일이 저장되었습니다.")