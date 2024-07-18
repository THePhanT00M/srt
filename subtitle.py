import logging  # 로그 기록을 위한 모듈

from tools.cli import cli  # 명령줄 인터페이스(CLI) 파싱을 위한 모듈
from tools.utils import extract_audio, transform, logging_print, remove_mr  # 유틸리티 함수들 임포트
from tools.transcript import generate_subtitles, matching_formats
from tools.visualize import visualizer

from models.whisperx.load import whisperx_result  # WhisperX 결과를 얻기 위한 함수 임포트
from models.SpeechBrain.load import speechMood  # SpeechBrain 감정 분석을 위한 함수 임포트

LOG_LEVEL = logging.INFO  # 로그 레벨 설정

def main():
    """
    프로그램의 메인 함수로, CLI 파싱, 오디오 추출 및 감정 분석 등의 작업을 수행합니다.
    """

    # 로깅 설정
    logging.basicConfig(level=LOG_LEVEL)

    try:
        # 명령줄 인자 파싱
        args = cli()  # cli() 함수는 명령줄 인자를 파싱하여 반환
        logging_print("Arguments parsed successfully.")  # 성공 메시지를 로그에 기록

        # 비디오에서 오디오 추출
        audio = extract_audio(args.input_path)  # extract_audio 함수 호출하여 오디오 추출
        print(audio)
        logging_print("Audio extracted successfully.")  # 성공 메시지를 로그에 기록

        audio = remove_mr(audio)

        # WhisperX 결과 얻기
        whispers = whisperx_result(audio)
        print(whispers)  # WhisperX 결과 출력
        logging_print("Whisper results obtained.")  # 성공 메시지를 로그에 기록

        # SpeechBrain 감정 분석 태그 얻기
        # speech_moods = speechMood(audio)
        # print(speech_moods)  # 감정 분석 결과 출력
        # logging_print("Speech Mood tags obtained.")  # 성공 메시지를 로그에 기록

        # 자막 생성
        subtitles = generate_subtitles(whispers)
        print(subtitles)
        logging_print('Subtitles obtained')

        # 자막을 원하는 형식으로 작성
        matching_formats(subtitles, args)
        logging_print("Subtitles written successfully.")

        # 시각화를 원하는 경우 시각화 수행
        if args.visualize:
            visualizer(subtitles, args)  # Visualizing if the argument is provided
            logging_print("Visualization completed.")
        else:
            logging_print("Transcript completed. No visualization.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")  # 예기치 않은 오류가 발생하면 오류 메시지를 로그에 기록

if __name__ == '__main__':
    main()  # 스크립트가 직접 실행될 때 main() 함수를 호출