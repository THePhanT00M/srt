from kiwipiepy import Kiwi, TypoTransformer, TypoDefinition
kiwi = Kiwi(model_type='sbg', typos='basic_with_continual')
kiwi.typo_cost_weight = 3
print(*kiwi.tokenize('자 물론 모든 분들이 실전과 유사하고 말하지만 사실 대부분 이제 길이가 비슷하다거나 선택이 구성비차다 이런 말씀 하시는데 더 중요한 건 정답에 대한 접근 방식이 너무 중요하거든요'))