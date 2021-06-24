# -*- coding: utf-8 -*-
"""NLP06.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10cQ6PZAj8lKUqqM38wNEb2_joqwJqUbv

# 글자 단위 RNN 언어 모델
"""

import numpy as np
import urllib.request
from tensorflow.keras.utils import to_categorical

urllib.request.urlretrieve("http://www.gutenberg.org/files/11/11-0.txt", filename="11-0.txt")

f = open('11-0.txt', 'rb')

lines = []

for line in f:
  line = line.strip() # strip을 통해 \r, \n을 제거
  line = line.lower() # 소문자화 
  line = line.decode('ascii', 'ignore') # \we2\x80\x99등과 같은 방
  if len(line)>0:
    lines.append(line)
f.close()

lines[:5]

text = ' '.join(lines)
print(f'문자열의 길이 또는 총 글자의 갯수 : {len(text)}')

print(text[:10])

# 글자 집합
char_vocab = sorted(list(set(text)))
vocab_size = len(char_vocab)

print(f'글자 집합의 크기 : {vocab_size}')

print(char_vocab)

# 글자 집합에 인덱스를 부여하고 전부 출력
char_to_index = dict((c,i) for i,c in enumerate(char_vocab))

print(char_to_index) # ~29 / 30~:26개 알파벳

# 인덱스로부터 글자 리턴
index_to_char = {}
for key, value in char_to_index.items():
  index_to_char[value] = key
  
print(index_to_char)

# train data 구성
seq_length = 60
n_samples = int(np.floor((len(text)-1)/seq_length)) # 내림함수/ceil/round/trunc

print(f'문장 샘플의 수 : {n_samples}')

"""Q&A
- 문자열을 60등분할때 길이 -1은 왜 하는건가요? 하는경우와 안하는경우 값은 똑같은데 꼭해야하나요?
- np.floor가 소수점은 버리는건데, text에서 -1한게 맨앞에 인덱스때문에 -1한걸로 알고 있어용. 작은 오차를 줄이기 위해 한것입니당. 그래서 np.floor를 하면 뒤에 소숫점들이 버리게 되므로 결과적으로 같은 값이 나오게 되는것이죠


"""

train_x = []
train_y = []

for i in range(n_samples): # 문장의 샘플 수(2658)만큼 수행
  x_sample = text[i * seq_length: (i+1) * seq_length] # 문장 샘플 하나씩
  x_encoded = [char_to_index[c] for c in x_sample] # 정수 인코딩(하나의 문장 샘플에 대해)
  train_x.append(x_encoded)

  y_sample = text[i*seq_length + 1: (i+1) *seq_length + 1] # 오른쪽으로 1칸 shift(이동)
  y_encoded = [char_to_index[c] for c in y_sample]
  train_y.append(y_encoded)

print(train_x[0])
print(train_y[0])

print(train_x[1])
print(train_y[1])

# One-hot encoding (np, to_catrgorical), 입력시퀀스에 대해 워드 임베딩 하지 않음 -> enbedding layer 사용 X
train_x = to_categorical(train_x)
train_y = to_categorical(train_y)

print(f'train_x 의 크기 (shape) : {train_x.shape}')
print(f'train_y 의 크기 (shape) : {train_y.shape}')

"""Sample의 수 : 2658\
Input Sequence Length (input_length) : 60\
Each Vector's Vimension (input_dim) : 56\
원-핫 벡터의 차원은 글자 집합의 크기인 56\
![](https://wikidocs.net/images/page/22886/rnn_image6between7.PNG)

# 모델 설계하기
"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, TimeDistributed

model = Sequential()
model.add(LSTM(256, input_shape=(None, train_x.shape[2]), return_sequences=True))
model.add(LSTM(256, return_sequences=True))
model.add(TimeDistributed(Dense(vocab_size, activation='softmax'))) # 다중 class 중 제일 값이 높은거 하나 뽑음 softmax

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics = ['accuracy'])
model.fit(train_x, train_y, epochs=80, verbose=1)

def sentence_generation(model, length):
  ix = [np.random.randint(vocab_size)] # 글자에 대한 랜덤 인덱스 생성
  y_char = [index_to_char[ix[-1]]] # 랜덤 익덱스로부터 글자 생성
  print(f'{ix[-1]}번 글자, {y_char}로 예측을 시작')
  X = np.zeros((1, length, vocab_size)) # (1, length, 55) 크기의 X 생성. 즉, LSTM의 입력 시퀀스 생성

  for i in range(length):
      X[0][i][ix[-1]] = 1 # X[0][i][예측한 글자의 인덱스] = 1, 즉, 예측 글자를 다음 입력 시퀀스에 추가
      print(index_to_char[ix[-1]], end="")
      ix = np.argmax(model.predict(X[:, :i+1, :])[0], 1)
      y_char.append(index_to_char[ix[-1]])
  return ('').join(y_char)

sentence_generation(model, 100)

sentence_generation(model, 30)

"""# 글자 단위 RNN (Char RNN)으로 텍스트 생성하기
다 대 일(many to one)구조의 RNN을 글자 다누이로 학습시키고, 텍스트 생성하기

## 데이터에 대한 이해와  전처리
"""

import numpy as np
from tensorflow.keras.utils import to_categorical

text='''
I get on with life as a programmer,
I like to contemplate beer.
But when I start to daydream,
My mind turns straight to wine.

Do I love wine more than beer?

I like to use words about beer.
But when I stop my talking,
My mind turns straight to wine.

I hate bugs and errors.
But I just think back to wine,
And I'm happy once again.

I like to hang out with programming and deep learning.
But when left alone,
My mind turns straight to wine.
'''

tokens = text.split() # \n 제거
text = ' '.join(tokens)
print(text)

char_vocab = sorted(list(set(text))) # 중복을 제거한 글자 집합 생성
print(char_vocab)

vocab_size = len(char_vocab)
print(f'글자 집합의 크기 : {vocab_size}')

char_to_index = dict((c,i) for i,c in enumerate(char_vocab)) # 글자에 고유한 정수 인덱스 부여
print(char_to_index)

"""example 5개의 입력 글자 시퀀스로부터 다음 글자 시퀀스를 예측 

- stude -> n  
- tuden -> t  
"""

length = 11
sequences = []
for i in range(length, len(text)):
  seq = text[i-length:i]
  sequences.append(seq)

print(f'총 훈련 샘플의 수: {len(sequences)}')

print(sequences)

# 전체 데이터에 대해 정수 인코딩
xx = []
for line in sequences: #전체 데이터에서 문장 샘플을 1개씩 꺼냄
  temp_x = [char_to_index[char] for char in line] # 문장 샘플에서 각 글자에 대해서 정수 인코딩 수행
  xx.append(temp_x)

for line in xx[:5]:
  print(line)

sequences = np.array(xx)
xx = sequences[:, :-1]
y = sequences[:, -1] # 맨 마지막 위치의 글자를 분리

for line in xx[:5]:
  print(line)

print(y[:5])

"""## 원-핫 인코딩 수행"""

sequences = [to_categorical(x, num_classes=vocab_size) for x in xx] # 변수 중볻돼서 바꿈 x -> xx

x = np.array(sequences)
y = to_categorical(y, num_classes=vocab_size) # y에 대한 원핫인코딩

print(x.shape)

"""- 샘플의 수 426
- 입력 시퀀스의 길이 10
- 각 벡터의 차원 33

## 모델 설계
"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.preprocessing.sequence import pad_sequences

model = Sequential()
model.add(LSTM(128, input_shape=(x.shape[1], x.shape[2]))) # (10, 33)
model.add(Dense(vocab_size, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer= 'adam', metrics=['accuracy'])
model.fit(x, y, epochs=100, verbose=1)

def sentence_generation(model, char_to_index, seq_length, seed_text, n):
  # 모델, 인덱스 정보, 문장 길이, 초기 시퀀스, 반복 횟수

  init_text = seed_text #문장 생성에 사용할 초기 시퀀스
  sentence = ''

  for _ in range(n): # n번 반복
    encoded = [char_to_index[char] for char in seed_text] #현재 시퀀스에 대한 정수 인코딩
    encoded = pad_sequences([encoded], maxlen=seq_length, padding='pre') #데이터에 대한 패딩
    encoded = to_categorical(encoded, num_classes=len(char_to_index))
    result = model.predict_classes(encoded, verbose=0)
    #입력한 x(현재 시퀀스)에 대해서 y를 예측하고 y(예측한 글자)를 result에 저장

    for char, index in char_to_index.items(): #만약 예측한 글자와 인덱스와 동일한 글자가 있다면
      if index == result: #해당 글자가 예측 글자이므로 break
        break
    
    seed_text = seed_text + char # 현재 시퀀스 + 예측 글자를 현재 시퀀스에 변경
    sentence = sentence + char # 예측 글자를 문장에 저장

  sentence = init_text + sentence
  return sentence

print(sentence_generation(model, char_to_index, 10, 'I get on w', 100))

print(sentence_generation(model, char_to_index, 10, 'Do I love wine', 100))

print(sentence_generation(model, char_to_index, 10, 'I like to hang', 100))



"""# 네이버 쇼핑 리뷰 감성 분석
- 총 200,000ro 리뷰로 구성  
- 평점이 5점 만점에 1, 2, 4, 5인 리뷰들로 구성
- 평점이 4, 5인 리뷰들에 긍정 1, 부정 0
- 감성 분류 수행

## Mecab
"""

!git clone https://github.com/SOMJANG/Mecab-ko-for-Google-Colab.git

cd Mecab-ko-for-Google-Colab

ls

!bash install_mecab-ko_on_colab190912.sh

from konlpy.tag import Mecab

mecab = Mecab()
print(mecab.morphs('노트북 사고 싶다'))

"""## 데이터 로드"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from collections import Counter
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

urllib.request.urlretrieve("https://raw.githubusercontent.com/bab2min/corpus/master/sentiment/naver_shopping.txt", filename="ratings_total.txt")

total_data = pd.read_table('ratings_total.txt', names=['ratings', 'reviews'])

print(f'total reviews number: {len(total_data)}')

total_data[:5]

"""훈련 데이터와 테스트 데이터 분리"""

total_data['label'] = np.select([total_data.ratings > 3], [1], default=0)
total_data[:5]

# 각 열에 중복을 제외한 샘플의 수를 카운트
total_data['ratings'].nunique(), total_data['reviews'].nunique(), total_data['label'].nunique()

total_data.drop_duplicates(subset=['reviews'], inplace=True) #reviews열에서 중복인 내용이 있다면 중복 제거
print('총 샘플의 수 : ',len(total_data))

# NULL값 유무
print(total_data.isnull().values.any())

# 훈련데이터와 테스트 데이터 3:1비율로 나눔
train_data, test_data = train_test_split(total_data, test_size = 0.25, random_state=42)
print('훈련용 리뷰의 갯수 : ', len(train_data))
print('테스트용 리뷰의 갯수 : ', len(test_data))

"""레이블 분포 확인"""

train_data['label'].value_counts().plot(kind='bar')

print(train_data.groupby('label').size().reset_index(name='count'))

"""## 데이터 정제

정규표현식을 사용하여 한글을 제외하고 모두 제거  
빈 샘플이 생겼는지 확인
"""

train_data['reviews'] = train_data['reviews'].str.replace("[^ㄱ-ㅎ ㅏ-ㅣ 가-힣]","")
train_data['reviews'].replace('', np.nan, inplace=True)
print(train_data.isnull().sum())

test_data.drop_duplicates(subset=['reviews'], inplace=True)
test_data['reviews'] = test_data['reviews'].str.replace("[^ㄱ-ㅎ ㅏ-ㅣ 가-힣]","")
test_data['reviews'].replace('', np.nan, inplace=True)
test_data = test_data.dropna(how='any')
print('전처리 후 테스트용 샘플의 갯수 : ',len(test_data))

"""## 토큰화"""

mecab = Mecab()

import warnings
warnings.filterwarnings('ignore')

"""### 불용어 제거"""

stopwords = ['도', '는', '다', '의', '가', '이', '은', '한', '에', '하', '고', '을', '를', '인', '듯', '과', '와', '네', '들', '듯', '지', '임', '게']

train_data['tokenized'] = train_data['reviews'].apply(mecab.morphs)
train_data['tokenized'] = train_data['tokenized'].apply(lambda x: [item for item in x if item not in stopwords])

test_data['tokenized'] = test_data['reviews'].apply(mecab.morphs)
test_data['tokenized'] = test_data['tokenized'].apply(lambda x: [item for item in x if item not in stopwords])

"""### 단어와 길이 분포 확인하기"""

negative_words = np.hstack(train_data[train_data.label == 0]['tokenized'].values)
positive_words = np.hstack(train_data[train_data.label == 1]['tokenized'].values)

# 각 단어 빈도수 계산 : Counter()
# 부정 리뷰에 대해 빈도가 높은 상위 20개 단어 출력
negative_word_count = Counter(negative_words)
print(negative_word_count.most_common(20))

# 각 단어 빈도수 계산 : Counter()
# 긍정 리뷰에 대해 빈도가 높은 상위 20개 단어 출력
positive_word_count = Counter(positive_words)
print(positive_word_count.most_common(20))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))
text_len = train_data[train_data['label']==1]['tokenized'].map(lambda x: len(x))
ax1.hist(text_len, color='red')
ax1.set_title('Positive Reviews')
ax1.set_xlabel('Length of sample')
ax1.set_ylabel('Number of samples')

print('Mean of Length of the Positive Rewivews :', np.mean(text_len))


text_len = train_data[train_data['label']==0]['tokenized'].map(lambda x: len(x))
ax2.hist(text_len, color='blue')
ax2.set_title('Negative Reviews')
fig.suptitle('Words in texts')
ax2.set_xlabel('Length of sample')
ax2.set_ylabel('Number of samples')

print('Mean of Length of the Negative Rewivews :', np.mean(text_len))

plt.show()

x_train = train_data['tokenized'].values
y_train = train_data['label'].values
x_test = test_data['tokenized'].values
y_test = test_data['label'].values

"""## 정수 인코딩"""

t = Tokenizer()
t.fit_on_texts(x_train)

threshold = 2
total_cnt = len(t.word_index) # Num of words
rare_cnt = 0 # 등장 빈도수가 threshold보다 작은 단어를 카운트
total_freq = 0 # 훈련 데이터의 전체 단어 빈도수 총 합
rare_freq = 0 # 등장 빈도수가 threshold보다 작은 단어의 등장 빈도수의 총 합

# Pair of word & freq To key & value
for key, value in t.word_counts.items():
  total_freq = total_freq+value

  if (value < threshold):
    rare_cnt = rare_cnt + 1
    rare_freq = rare_freq + value


print('단어 집합(vocabulary)의 크기 :', total_cnt)
print('등장 빈도가 %s번 이하인 희귀단어의 수: %s '% (threshold-1, rare_cnt))
print('단어 집합에서 희귀 단어의 비율 :', (rare_cnt/ total_cnt)*100)
print('전체 등장 빈도에서 희귀단어 등장 빈도 비율: ',(rare_freq/total_freq)*100)

# 전체 단어 갯수 중 빈도수 2 이하인 단어 갯수 제거
# 0번 패딩 토큰고 1번 OOV토큰을 고려해서 +2
vocab_size = total_cnt - rare_cnt + 2
print('Vocab Size :', vocab_size)

original_vocab_size = vocab_size + rare_cnt - 2
print('Original Vocab Size :', original_vocab_size)

tokenizer = Tokenizer(vocab_size, oov_token='OOV')
tokenizer.fit_on_texts(x_train)

x_train = tokenizer.texts_to_sequences(x_train)
x_test = tokenizer.texts_to_sequences(x_test)

print(x_train[:3])
print(x_test[:3])

"""## 패딩"""

print('리뷰의 최대 길이 :', max(len(l) for l in x_train))
print('리뷰의 평균 길이 :', sum(map(len, x_train))/len(x_train))
plt.hist([len(s) for s in x_train], bins=50)
plt.xlabel('length of smaples')
plt.ylabel('number of sample')
plt.show()

def below_threshold_len(max_len, nested_list):
  cnt=0
  for s in nested_list:
    if (len(s) <= max_len):
      cnt = cnt + 1
  print(f'전체 샘플 중 길이가 {max_len}이하인 샘플의 비율 : {(cnt/len(nested_list))*100}')
  
  # print('전체 샘플 중 길이가 %s 이하인 샘플의 비율 : %s'%(max_len, (cnt/len(nested_list))*100))

max_len = 80
below_threshold_len(max_len, x_train)

x_train = pad_sequences(x_train, maxlen= max_len)
x_test = pad_sequences(x_test, maxlen=max_len)

print(x_train.shape)
print(x_test.shape)

"""### GRU 모델로 학습하기"""

from tensorflow.keras.layers import Embedding, Dense, GRU
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

model = Sequential()

model.add(Embedding(vocab_size, 100))
model.add(GRU(128))
model.add(Dense(1, activation='sigmoid')) # 다중분류가 아니니 softmax X

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=4)
mc = ModelCheckpoint('best_model.h5', monitor='val_acc', mode='max', verbose=1, save_best_only=True)

# compile
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
history = model.fit(x_train, y_train, epochs= 30, callbacks=[es, mc], batch_size = 60, validation_split=0.2)

loaded_model = load_model('best_model.h5')
print('\n 테스트 정확도 : %.4f'% (loaded_model.evaluate(x_test, y_test)[1]))

"""## 리뷰 예측하기"""

def sentiment_predict(new_sentence):
  new_sentence = mecab.morphs(new_sentence) #토큰화
  new_sentence = [word for word in new_sentence if not word in stopwords] #불용어 제거
  encoded = tokenizer.texts_to_sequences([new_sentence])
  pad_new = pad_sequences(encoded, maxlen=max_len) # 패딩

  score = float(loaded_model.predict(pad_new)) #d예측

  if (score > 0.5):
    print('{:.2f}%확률로 긍정 리뷰입니다. '.format(score*100))
  else:
    print(f'{(1-score)*100:.2f}%의 확률로 부정 리뷰입니다.')

sentiment_predict('이 상품 진짜 좋아요.. 저는 강추 대박')

sentiment_predict('이 상품 별로에요..')

sentiment_predict('강아지 고양이')

sentiment_predict('감자 고구마 치킨')

sentiment_predict('사이다')

"""# 글자 단위(Character-level)로 구현한 seq2seq 번역기

Character-Level Neural Machine Translation\
https://wikidocs.net/24996
"""

!pwd

cd ../

import os
import pandas as pd
file_path = '/content/drive/MyDrive/NLP/fra.txt'
lines = pd.read_csv(file_path, names=['eng', 'fra', 'cc'], sep='\t')
lines.sample(5)

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import numpy as np

lines = lines[['eng', 'fra']][:50000] # col을 drop 해보기
lines.sample(5)

# 시작토큰과 종료 토큰 추가
sos_token = '\t'
eos_token = '\n'
lines.fra = lines.fra.apply(lambda x: '\t' + x + '\n')
print('전체 샘플의 수 :',len(lines))
lines.sample(5)

# 글자 단위로 토큰화
eng_tokenizer = Tokenizer(char_level=True)

# 5만개의 행을 가진 eng의 각 행에 토큰화 수행
eng_tokenizer.fit_on_texts(lines.eng)

# 단어를 숫자값 인덱스로 변환하여 저장
input_text = eng_tokenizer.texts_to_sequences(lines.eng)

input_text[:3]

fra_tokenizer = Tokenizer(char_level=True)
# 글자 단위로 토큰화
fra_tokenizer.fit_on_texts(lines.fra)
# 50000개의 행을 가진 eng의 각 행에 토큰화 수행
target_text = fra_tokenizer.texts_to_sequences(lines.fra)
# 단어를 숫자값 인덱스로 변환하여 저장
target_text[:3]

eng_vocab_size = len(eng_tokenizer.word_index) + 1
fra_vocab_size = len(fra_tokenizer.word_index) + 1

print('영어 단어장의 크기 :',eng_vocab_size)
print('프랑스어 단어장의 크기 :', fra_vocab_size)

# 최대길이 -> padding
max_eng_seq_len = max([len(line) for line in input_text])
max_fra_seq_len = max([len(line) for line in target_text])

print('영어 시퀀스의 최대 길이', max_eng_seq_len)
print('프랑스 시퀀스의 최대 길이', max_fra_seq_len)

print('전체 샘플의 수 :', len(lines))
print('영어 단어장의 크기:', eng_vocab_size)
print('프랑스어 단어장의 크기:', fra_vocab_size)
print('영어 시퀀스의 최대 길이:', max_eng_seq_len)
print('프랑스 시퀀스의 최대 길이', max_fra_seq_len)

encoder_input = input_text

# 종료 토큰 제거
decoder_input = [[char for char in line if char != fra_tokenizer.word_index[eos_token]] for line in target_text]
# 시작 토큰 제거
decoder_target = [[char for char in line if char != fra_tokenizer.word_index[sos_token]] for line in target_text]

print(decoder_input[:3]) # <eos>토큰 제거
print(decoder_target[:3]) # <sos>토큰 제거

encoder_input = pad_sequences(encoder_input, maxlen=max_eng_seq_len, padding='post')
decoder_input = pad_sequences(decoder_input, maxlen=max_fra_seq_len, padding='post')
decoder_target = pad_sequences(decoder_target, maxlen=max_fra_seq_len, padding='post')

print('영어 데이터의 크기(shape) :', np.shape(encoder_input))
print('프랑스어 입력데이터의 크기 : ', np.shape(decoder_input))
print('프랑스어 출력데이터의 크기 : ', np.shape(decoder_target))

print(input_text[0])
print(encoder_input[0])

encoder_input = to_categorical(encoder_input)
decoder_input = to_categorical(decoder_input)

decoder_target = to_categorical(decoder_target)

print(f'영어 입력 데이터의 크기 : {np.shape(encoder_input)}')
print('프랑스어 입력데이터의 크기 : ', np.shape(decoder_input))
print('프랑스어 출력데이터의 크기 :', np.shape(decoder_target)) # 샘플의 수 x 샘플의 길이 x 단어장의 크기

# validation
n_of_val = 3000

encoder_input_train = encoder_input[:-n_of_val]
decoder_input_train = decoder_input[:-n_of_val]
decoder_target_train = decoder_target[:-n_of_val]


encoder_input_test = encoder_input[-n_of_val:]
decoder_input_test = decoder_input[-n_of_val:]
decoder_target_test = decoder_target[-n_of_val:]

print('영어 학습 데이터의 크기 :', np.shape(encoder_input))
print('프랑스어 학습 입력 데이터의 크기 :', np.shape(decoder_input))
print('프랑스어 학습 출력 데이터의 크기 :', np.shape(decoder_target))

"""## 모델 훈련하기

"""

from tensorflow.keras.layers import Input, LSTM, Embedding, Dense
from tensorflow.keras.models import Model

# LSTM셀의 마지막 time step의 hidden state와 cell state를 디코더 LSTM의 첫번째 hidden state와 cell state 전달해주자

# 입력 텐서를 생성
encoder_inputs = Input(shape=(None, eng_vocab_size))

# hidden state 256인 LSTM을 생성
encoder_lstm = LSTM(units=256, return_state=True)

# 디코더로 전달할 hidden state, cell state를 리턴. encoder_output은 여기서는 불필요.
encoder_outputs, state_h, state_c = encoder_lstm(encoder_inputs)

# hidden state와 cell state를 다음 time step으로 전달하기 위해서 별도로 저장
encoder_states = [state_h, state_c]

# Decoder

# 입력 텐서를 생성
decoder_inputs = Input(shape=(None, fra_vocab_size))

# hidden state size 256인 decoder LSTM을 생성
decoder_lstm = LSTM(units=256, return_sequences=True, return_state=True)

# decoder의 output은 모든 timestep의 hidden state
decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state = encoder_states)

decoder_softmax_layer = Dense(fra_vocab_size, activation='softmax')
decoder_outputs = decoder_softmax_layer(decoder_outputs)

# 모델을 합침, 아웃풋=decoder의 output
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

model.compile(optimizer="rmsprop", loss="categorical_crossentropy")
model.summary() # input_(num) 이 왜 다르게 나옴?

model.fit(x=[encoder_input_train, decoder_input_train], y=decoder_target_train, validation_data=([encoder_input_test, decoder_input_test], decoder_target_test), batch_size=128, epochs=30)

"""## 모델 테스트

훈련시에 학습해야할 타겟 문장을 디코더 모델의 입력, 출력 시퀀스로 넣어주고, 디코더 모델이 타겟문장을 한꺼번에 출력하게 할 수 있습니다. 테스트 단계는 불가능!

테스트 단계에서 디코더 동작 순서
- 인코더에 입력 문장을 넣어 마지막 time step의 hidden, cell state를 얻는다.
- 토큰인 \t를 디코더에 입력한다.
- 이전 timestep의 출력층의 예측결과를 현재 timestep의 입력으로 한다.
- 3을 반복하다가 토큰인 \n가 예측되면 이를 중단한다.
"""

encoder_model = Model(inputs=encoder_inputs, outputs=encoder_states)
encoder_model.summary()

decoder_state_input_h = Input(shape=(256,))
# 이전 timestep의 hidden state를 저장하는 텐서
decoder_state_input_c = Input(shape=(256,))
# 이전 timestep의 cell state를 저장하는 텐서
decoder_state_inputs = [decoder_state_input_h, decoder_state_input_c]
# 이전 time step의 hidden state와 cell state를 하나의 변수에 저장

# decoder_state_inputs를 현재 time step의 초기상태로 사용
decoder_outputs, state_h, state_c = decoder_lstm(decoder_inputs, initial_state=decoder_state_inputs)
# 현재 time step의 hidden state와 cell state를 하나의 변수에 저장
decoder_states = [state_h, state_c]

decoder_outputs = decoder_softmax_layer(decoder_outputs)
decoder_model= Model(inputs=[decoder_inputs] + decoder_state_inputs, outputs=[decoder_outputs]+decoder_states)
decoder_model.summary()

eng2idx = eng_tokenizer.word_index
fra2idx = fra_tokenizer.word_index
idx2eng = eng_tokenizer.index_word
idx2fra = fra_tokenizer.index_word

def decode_sequence(input_seq):
  states_value = encoder_model.predict(input_seq)

  target_seq = np.zeros((1, 1, fra_vocab_size))
  target_seq[0, 0, fra2idx['\t']] =1

  stop_condition = False
  decoded_sentence = ""

  while not stop_condition:
    output_tokens, h, c = decoder_model.predict([target_seq]+ states_value)

    sampled_token_index = np.argmax(output_tokens[0, -1, :])
    sampled_char = idx2fra[sampled_token_index]

    decoded_sentence += sampled_char

    if (sampled_char == '\n' or
        len(decoded_sentence) > max_fra_seq_len):
      stop_condition = True

    target_seq = np.zeros((1, 1, fra_vocab_size))
    target_seq[0, 0, sampled_token_index] =1

    states_value = [h, c]
  return decoded_sentence

import numpy as np
for seq_index in [3, 50, 100, 300, 1001]:
  # 입력 문장의 인덱스 (자유롭게 바꿔서 테스트 해보세요!)
  input_seq = encoder_input[seq_index: seq_index +1]
  decoded_sentence = decode_sequence(input_seq)
  print(35 * "-")
  print('입력 문장 :', lines.eng[seq_index])
  print('정답 문장 :', lines.fra[seq_index][1:len(lines.fra[seq_index])-1])
  # '\t'와 '\n'을 빼고 출력
  print('번역기가 번역한 문장 :', decoded_sentence[:len(decoded_sentence)-1])
  # '\n'을 빼고 출력
