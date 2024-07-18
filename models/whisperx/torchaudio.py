import torchaudio
import torchaudio.transforms as transforms

def preprocess_audio(file_path):
    waveform, sample_rate = torchaudio.load(file_path)
    # 전처리: 모노로 변환, 리샘플링
    waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform.mean(dim=0, keepdim=True))
    return waveform, 16000

def augment_audio(waveform, sample_rate):
    # 데이터 증강: 타임 스트레치, 피치 쉬프트 등
    augmentations = transforms.Compose([
        transforms.TimeStretch(),
        transforms.FrequencyMasking(freq_mask_param=30),
        transforms.TimeMasking(time_mask_param=50)
    ])
    augmented_waveform = augmentations(waveform)
    return augmented_waveform, sample_rate