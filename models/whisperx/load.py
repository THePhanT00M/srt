import whisperx  # WhisperX 모델을 사용하기 위한 라이브러리
import json  # JSON 파일을 처리하기 위한 모듈
from tools.cli import cli  # 명령줄 인터페이스(CLI) 파싱을 위한 모듈
import torch

def whisperx_result(audio_path, language='ko', api_keys='./assets/api_key.json'):
    """
    WhisperX 모델을 사용하여 주어진 오디오 파일을 텍스트로 변환하고, 텍스트를 정렬합니다.

    매개변수:
    audio_path (str): 텍스트로 변환할 오디오 파일의 경로
    language (str, optional): 오디오 파일의 언어. 기본값은 'ko' (한국어)
    api_keys (str, optional): API 키가 저장된 JSON 파일의 경로. 기본값은 './assets/api_key.json'

    반환값:
    list: 정렬된 텍스트 세그먼트 리스트
    """
    args = cli()  # 명령줄 인자 파싱

    # Hugging Face 사용자 토큰을 가져오기 위해 API 키 파일 열기
    with open(api_keys, 'rb') as fr:
        apifile = json.load(fr)
    my_token = apifile['hf_token']  # 토큰 추출

    # WhisperX 추론 옵션 설정
    options = dict(language=language, beam_size=5, best_of=5)
    transcribe_options = dict(task="transcribe", **options)

    # WhisperX 모델 로드
    model = whisperx.load_model("large-v3", device=args.device, compute_type=args.compute_type)
    model = torch.nn.DataParallel(model)
    audio = whisperx.load_audio(audio_path)  # 오디오 파일 로드

    # WhisperX 출력 정렬
    result = model.transcribe(audio, batch_size=args.batch_size)  # 오디오 텍스트 변환
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=args.device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device=args.device, return_char_alignments=False)

    # 화자 분할을 원할 경우, 다음 라인의 주석을 해제

    # 화자 레이블 할당
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=my_token, device=args.device)
    # 알 수 있는 경우 화자의 최소/최대 수 추가
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    return result['segments']  # 정렬된 텍스트 세그먼트 반환