import pydub
import wave
import subprocess  # 외부 프로그램 실행을 위한 모듈
import os  # 파일 및 디렉토리 관련 작업을 위한 모듈
import pandas as pd
import ast
import logging
from demucs import pretrained
from demucs.apply import apply_model
from demucs.audio import AudioFile
import soundfile as sf

logging.basicConfig(level=logging.ERROR)

def split_audio(file_path, segment_length_ms, output_folder):
    """
    file_path: 오디오 파일의 경로 (예: "sample.mp3")
    segment_length_ms: 나눌 각 부분의 길이 (밀리초 단위)
    output_folder: 출력할 폴더의 경로
    """

    audio = pydub.AudioSegment.from_file(file_path, format="mp3")
    total_length = len(audio)

    for i in range(0, total_length, segment_length_ms):
        segment = audio[i:i+segment_length_ms]
        segment.export(f"{output_folder}/segment_{i//segment_length_ms}.mp3", format="mp3")
        print(f"Saved: segment_{i//segment_length_ms}.mp3")

    print("All segments saved!")


def mp3towav(mp3_path, wav_path):
    """
    mp3_path : 입력 오디오 파일의 경로
    wav_path : 출력 오디오 파일의 경로
    """
    sound = pydub.AudioSegment.from_mp3(mp3_path)
    sound.export(wav_path, format="wav")


def get_duration(audio_path):

    audio = wave.open(audio_path)
    frames = audio.getnframes()
    rate = audio.getframerate()
    duration = frames / float(rate)
    return duration

def extract_audio_and_remove_background(input_file: str, output_file: str = './dataset/audio/no_mr_audio.mp3') -> str:
    """
    주어진 비디오 파일에서 오디오를 추출하고 MR을 제거하여 mp3 파일로 저장합니다.

    매개변수:
    input_file (str): 오디오를 추출할 비디오 파일의 경로
    output_file (str, optional): MR이 제거된 오디오를 저장할 파일의 경로. 기본값은 './dataset/audio/no_mr_audio.mp3'

    반환값:
    str: MR이 제거된 오디오 파일의 경로
    """

    # 임시 파일 경로 설정
    temp_audio_file = './temp_extracted_audio.wav'

    # 출력 파일의 디렉토리를 생성
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # ffmpeg 명령어를 구성하는 리스트 (16-bit WAV로 추출)
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '44100',
        '-ac', '2',
        temp_audio_file
    ]

    # ffmpeg 명령어 실행
    subprocess.run(cmd, input='y\n', text=True)

    # Demucs 모델 불러오기
    model = pretrained.get_model('htdemucs')
    model.eval()

    # 오디오 파일 읽기
    wav = AudioFile(temp_audio_file).read(streams=0, samplerate=44100, channels=2)

    # Demucs 모델을 사용하여 오디오 분리
    sources = apply_model(model, wav.unsqueeze(0), split=True, overlap=0.25)[0]

    # 분리된 보컬 트랙 저장
    vocals = sources[model.sources.index('vocals')].cpu().squeeze().numpy()
    vocal_path = os.path.splitext(output_file)[0] + '_vocals.wav'

    # `soundfile`을 사용하여 오디오 파일로 저장
    sf.write(vocal_path, vocals.T, 44100)

    # ffmpeg를 사용하여 분리된 보컬 트랙을 mp3로 변환하여 저장
    cmd = [
        'ffmpeg',
        '-i', vocal_path,
        output_file
    ]
    subprocess.run(cmd, input='y\n', text=True)

    # 임시 파일 삭제
    os.remove(temp_audio_file)
    os.remove(vocal_path)

    # MR이 제거된 오디오 파일의 경로를 반환
    return output_file

def extract_audio(input_file, output_file='./dataset/audio/extracted_audio.mp3'):
    """
    주어진 비디오 파일에서 오디오를 추출하여 mp3 파일로 저장합니다.

    매개변수:
    input_file (str): 오디오를 추출할 비디오 파일의 경로
    output_file (str, optional): 추출된 오디오를 저장할 파일의 경로. 기본값은 './dataset/audio/extracted_audio.mp3'

    반환값:
    str: 추출된 오디오 파일의 경로
    """

    # 출력 파일의 디렉토리를 생성
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # ffmpeg 명령어를 구성하는 리스트
    cmd = [
        'ffmpeg',   # ffmpeg 프로그램
        '-i', input_file,  # 입력 파일을 지정
        '-vn',  # 비디오 트랙을 사용하지 않음 (오디오만 추출)
        output_file  # 출력 파일 경로를 지정
    ]

    # subprocess.run() 함수를 사용하여 ffmpeg 명령어를 실행
    # input='y\n'은 어떤 사용자 입력이 필요할 때 'y'를 입력하도록 함
    # text=True는 입력 및 출력이 문자열 형식임을 지정
    subprocess.run(cmd, input='y\n', text=True)

    # 추출된 오디오 파일의 경로를 반환
    return output_file

def remove_mr(input_audio, output_audio='./dataset/audio/no_mr_audio.mp3'):
    """
    주어진 오디오 파일에서 MR을 제거하여 저장합니다.

    매개변수:
    input_audio (str): MR을 제거할 오디오 파일의 경로
    output_audio (str, optional): MR이 제거된 오디오를 저장할 파일의 경로. 기본값은 './dataset/audio/no_mr_audio.mp3'

    반환값:
    str: MR이 제거된 오디오 파일의 경로
    """
    # Demucs 모델 불러오기
    model = pretrained.get_model('htdemucs')
    model.eval()

    # 오디오 파일 읽기
    wav = AudioFile(input_audio).read(streams=0, samplerate=44100, channels=2)

    # Demucs 모델을 사용하여 오디오 분리
    sources = apply_model(model, wav.unsqueeze(0), split=True, overlap=0.25)[0]

    # 분리된 보컬 트랙 저장
    vocals = sources[model.sources.index('vocals')].cpu().squeeze().numpy()
    vocal_path = os.path.splitext(output_audio)[0] + '_vocals.wav'

    # `soundfile`을 사용하여 오디오 파일로 저장
    sf.write(vocal_path, vocals.T, 44100)

    # ffmpeg를 사용하여 분리된 보컬 트랙을 mp3로 변환하여 저장
    output_dir = os.path.dirname(output_audio)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cmd = [
        'ffmpeg',
        '-i', vocal_path,
        output_audio
    ]
    subprocess.run(cmd, input='y\n', text=True)

    # MR이 제거된 오디오 파일의 경로를 반환
    return output_audio

def trim_video(input_file, start, end, output_file = './dataset/video/trimed_output.mp4'):

    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start,
        '-to', end,
        '-c copy', output_file
    ]
    subprocess.call(cmd)

    return output_file

def trim_audio(input_file, start, end, output_file = './dataset/audio/trimed_audio.mp3'):
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start,
        '-to', end,
        '-c copy', output_file
    ]
    subprocess.call(cmd)

    return output_file

def transform(csv_path):

    results = pd.read_csv(csv_path)

    transformed_data = []

    for idx, row in results.iterrows():
        tags = ast.literal_eval(row['tags'])
        for tag in tags:
            transformed_data.append({
                'probability': tag['probability'],
                'name': tag['name'],
                'start_time': row['start_time'],
                'end_time': row['end_time']
            })

    transformed_df = pd.DataFrame(transformed_data)
    transformed_df['name_code'] = transformed_df['name'].astype('category').cat.codes

    return transformed_df


def logging_print(input):
    print("-"*50)
    print(input)
    print("-"*50)


def format_time(seconds):
    # 시간을 SRT 형식 (hh:mm:ss,ms)으로 포맷팅
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"



def emotion_to_text(emotion):
    """Convert emotion code to text description."""
    emotion_mapping = {
        'h': 'happy',
        'n': 'neutral',
        'a': 'angry',
        's': 'sad'
    }
    return emotion_mapping[emotion]
