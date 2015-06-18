from __future__ import print_function
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.layers.recurrent import LSTM
from keras.datasets.data_utils import get_file
import numpy as np
import random, sys
import cPickle as pickle

# helper function to sample an index from a probability array
def sample(a, diversity=0.75):
	if random.random() > diversity:
		return np.argmax(a)
	while 1:
		i = random.randint(0, len(a)-1)
		if a[i] > random.random():
			return i


'''
	Example script to generate text from Nietzsche's writings.

	At least 20 epochs are required before the generated text
	starts sounding coherent.

	It is recommended to run this script on GPU, as recurrent
	networks are quite computationally intensive.

	If you try this script on new data, make sure your corpus 
	has at least ~100k characters. ~1M is better.
'''

replays = pickle.load(open("parsed_games.pkl","rb"))
print('corpus length:', len(replays["streams"]))

text = list(zip(*replays["streams"])[1])
chars = replays["actions"].values()
print('total chars:', len(chars))
char_indices = replays["symbols"]
indices_char = replays["actions"]

games = []
gamestart = 0
gamelens = []
print("Splitting stream by game...")
for i in range(0,len(text)):
	if text[i] == char_indices["GAMEOVER()"]:
		games.append(text[gamestart:i+1])
		gamelens.append(len(games[-1]))
		gamestart = i+1
print('#games:', len(games))

###This code trains on each game as its own sequence, padding with GAMEOVER() characters to equalise game lengths.
maxlen = max(gamelens)
sentences = []
next_chars = []
for g in games:
	sentences.append(g+(char_indices["GAMEOVER()"] * (maxlen-len(g))))
	next_chars.append[sentences[-1][1:]]
print('#sequences:', len(sentences))

print('Vectorization...')
X = np.zeros((len(sentences), maxlen, len(chars)))
y = np.zeros((len(sentences), maxlen, len(chars)))
for i, sentence in enumerate(sentences):
	for t, char in enumerate(sentence):
		X[i, t, char] = 1.
	y[i, :-1, :] = X[i, 1:, :]
	y[i, maxlen-1,char_indices["GAMEOVER()"]] = 1

###This code redundantly subsamples each game into length maxlen sequences
#maxlen = 30
#step = 3
#sentences = []
#next_chars = []
#for g in games:
#	for i in range(0,len(g)-maxlen, step):
#		sentences.append(g[i:i+maxlen])
#		next_chars.append(g[i+maxlen])
#print('#sequences:', len(sentences))

'''
# cut the text in semi-redundant sequences of 30 characters

maxlen = 30
step = 5
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
	sentences.append(text[i : i + maxlen])
	next_chars.append(text[i + maxlen])
print('nb sequences:', len(sentences))

print('Vectorization...')
X = np.zeros((len(sentences), maxlen, len(chars)))
y = np.zeros((len(sentences), len(chars)))
for i, sentence in enumerate(sentences):
	for t, char in enumerate(sentence):
		X[i, t, char] = 1.
	y[i, next_chars[i]] = 1.
'''

	

# build the model: 2 stacked LSTM
print('Build model...')
model = Sequential()
model.add(LSTM(len(chars), 512, return_sequences=True))
model.add(LSTM(512, 512, return_sequences=True))
model.add(TimeDistributedDense(512, len(chars), activation='time_distributed_softmax'))

model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

# train the model, output generated text after each epoch
for iteration in range(1, 50):
	print()
	print('-' * 50)
	print('Iteration', iteration)
	model.fit(X, y, batch_size=128, nb_epoch=1)

	seed_game = random.randint(0,len(games))
	###start_index = random.randint(0, len(text) - maxlen - 1)

	for diversity in [0.4, 0.7, 1.]:
		print()
		print('----- diversity:', diversity)

		generated = []
		sentence = games[seed_game][0:maxlen]
		###sentence = text[start_index : start_index + maxlen]
		#print(sentence)
		generated += [indices_char[s] for s in sentence]
		generated = generated[:generated.index("GAMEOVER()")+1]
		print('----- Generating with seed: "' + ", ".join(generated) + '"')

		x = np.zeros((1, maxlen, len(chars)))
		for t, char in enumerate(sentence):
			x[0, t, char] = 1.
		preds = model.predict(x,verbose=1)
		sys.stdout.write("Predicting: "+", ".join([indices_chars[p] for p in preds])

		sys.stdout.flush()
		'''
		for iteration in range(400):
			x = np.zeros((1, maxlen, len(chars)))
			for t, char in enumerate(sentence):
				x[0, t, char] = 1.

			preds = model.predict(x, verbose=0)[0]
			next_index = sample(preds, diversity)
			next_char = indices_char[next_index]

			generated.append(next_char)
			sentence = sentence[1:]
			sentence.append(next_index)

			sys.stdout.write(", "+next_char)
			sys.stdout.flush()
			if next_char == "GAMEOVER()":
				break
		'''
		print()

