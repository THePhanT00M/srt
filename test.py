import re

def filter_hesitation(text):
    # 간투어를 나타내는 패턴 정의
    hesitation_patterns = [
        r'\b음\b', r'\b어\b', r'\b저\b', r'\b그\b', r'\b음...\b', r'\b어...\b'
    ]
    for pattern in hesitation_patterns:
        text = re.sub(pattern, '', text)
    return text

def filter_redundant_phrases(text):
    # 동일한 단어가 연속으로 반복되는 경우 필터링
    redundant_pattern = re.compile(r'\b(\w+)\s*\1+\b')
    text = redundant_pattern.sub(r'\1', text)

    # 다음 단어의 첫 글자가 같은 경우 필터링
    similar_start_pattern = re.compile(r'\b(\w)(\w*)\s+\1(\w*)\b')
    text = similar_start_pattern.sub(r'\1\3', text)

    # 두 단어가 동일한 경우 필터링
    redundant_two_words_pattern = re.compile(r'\b(\w+)\s+\1\b')
    text = redundant_two_words_pattern.sub(r'\1', text)

    return text

def filter_text(text):
    # 머뭇거리는 표현 필터링
    text = filter_hesitation(text)
    # 중복 발화 필터링
    text = filter_redundant_phrases(text)
    return text

# 테스트
sample_text = "음 이거는 저 저 이번에 어 어 새로운 프로젝트 입니다. 그 그 우리가 해야 할 일은 많습니다. 응응응 우 우리 우리 하는 일이 많습니다. 우리 번호 우리 번호가 두번 나옵니다."
filtered_text = filter_text(sample_text)
print("필터링 전:", sample_text)
print("필터링 후:", filtered_text)