from gensim.models import Word2Vec
import os
import re
import numpy as np
from konlpy.tag import Okt


# 단어 유사도를 계산하는 함수
def calculate_word_similarity(path, words_list):
	files = os.listdir(path)
	target_file = ""
	words_list = [word for word in words_list if len(word) != 0]
	
	for file in files:
		if re.search("\.model$",file):
			target_file = file
			break
		else:
			continue

	try:
		model = Word2Vec.load(path + target_file)
	except:
		return "path or type error"
	
	try:
		silmilar_list = model.wv.most_similar(positive=words_list, topn=30)
		silmilar_list = [f"{idx+1}. 단어: {cur[0]} / 유사도: {cur[1]*100:.3f}%" for idx, cur in enumerate(silmilar_list)]
	except:
		return "model error"
	
	return silmilar_list


# 문장벡터를 생성하는 함수
def get_sentence_vector(model, word_list):
	#문장에 포함된 단어벡터 담는 리스트
	words_vec = []
	for word in word_list:
		try:
			vec = model.wv.get_vector(word)
			words_vec.append(vec)
		except:
			continue
	
	# 문장벡터 생성 (평균)
	if len(words_vec) == 0:
		sent_vec = np.zeros(300)
	else:
		sent_vec = np.array(words_vec).mean(axis = 0)

	return sent_vec


# 유사도를 계산하는 함수
def get_similarity(sent_vec1, sent_vec2):
    similarity = np.dot(sent_vec1, sent_vec2) / (np.linalg.norm(sent_vec1) * np.linalg.norm(sent_vec2))
    return similarity


# 문장 유사도를 계산하는 함수
def calculate_sentence_similarity(path, target_sentence, sentence_list):
	files = os.listdir(path)
	target_file = ""
	
	for file in files:
		if re.search("\.model$",file):
			target_file = file
			break
		else:
			continue
	
	try:
		model = Word2Vec.load(path + target_file)
	except:
		return "path or type error"
	
	try:
		okt = Okt()
		target_vector = get_sentence_vector(model, okt.morphs(target_sentence))
		sentence_vector_list = [get_sentence_vector(model, okt.morphs(sentence)) for sentence in sentence_list]
		
		silmilar_list = []
		for sentence_vector in sentence_vector_list:
			silmilar_list.append(get_similarity(target_vector, sentence_vector))

		silmilar_list = [f"{sentence_list[idx]} / 유사도: {cur*100:.3f}%" for idx, cur in enumerate(silmilar_list)]

	except:
		return "model error"
	
	return silmilar_list


# 테스트
if __name__ == "__main__":
	path = "C:/Users/Admin/Desktop/KMU/4-1학기/웹클라이언트컴퓨팅/과제/word-e-back/word_e/data_client/model_25/"
	words_list = ["멋진","남자"]
	print(calculate_word_similarity(path, words_list))
	print(calculate_sentence_similarity(path, "나는 사람이다.", ["나는 인간이다","","나는 밥을 먹는다","식물은 밥에서 채소가 된다"]))
