from speechbrain.inference.interfaces import foreign_class
from speechbrain.inference.diarization import Speech_Emotion_Diarization

def speechMood(audio):
    """
    주어진 오디오 파일에서 감정 분석을 수행하여 결과를 반환합니다.

    매개변수:
    audio (str): 감정 분석을 수행할 오디오 파일의 경로

    반환값:
    dict: 감정 다이어리 결과
    """
    # 추출된 오디오 파일의 경로 설정
    audio_path = './dataset/audio/extracted_audio.mp3'

    # SpeechBrain 감정 다이어리 모델 로드
    classifier = Speech_Emotion_Diarization.from_hparams(
        source="speechbrain/emotion-diarization-wavlm-large"  # 모델 소스 지정
    )

    # 오디오 파일에서 감정 분석 수행
    diary = classifier.diarize_file(audio)

    # 감정 다이어리 결과 반환
    return diary[audio_path]