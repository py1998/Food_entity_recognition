import pandas as pd
import numpy as np
import string
from string import digits
import matplotlib.pyplot as plt
import re
from sklearn.model_selection import train_test_split
from keras.layers import Input, LSTM, Embedding, Dense
from keras.models import Model
from keras.utils import plot_model


Lines=pd.read_csv("Generate.csv")
lines_eng=Lines.question
lines_fr=Lines.answer
lines_eng=lines_eng.apply(lambda x: x.lower())
lines_fr=lines_fr.apply(lambda x: x.lower())

lines_eng=lines_eng.apply(lambda x: re.sub("'", '', x)).apply(lambda x: re.sub(",", ' COMMA', x))
lines_fr=lines_fr.apply(lambda x: re.sub("'", '', x)).apply(lambda x: re.sub(",", ' COMMA', x))

exclude = set(string.punctuation)
lines_eng=lines_eng.apply(lambda x: ''.join(ch for ch in x if ch not in exclude))
lines_fr=lines_fr.apply(lambda x: ''.join(ch for ch in x if ch not in exclude))

# remove_digits = string.maketrans('', '', digits)
# delete_chars=''.join(chr(i) for i in xrange(32))
# lines.eng=lines.eng.apply(lambda x: x.translate(None,delete_chars))
# lines.fr=lines.fr.apply(lambda x: x.translate(None,delete_chars))


lines_fr = lines_fr.apply(lambda x : 'START_'+" "+ x + " "+'_END')

all_eng_words = set()
for eng in lines_eng:
    for word in eng.split():
        if word not in all_eng_words:
            all_eng_words.add(word)

all_french_words = set()
for fr in lines_fr:
    for word in fr.split():
        if word not in all_french_words:
            all_french_words.add(word)

lenght_list=[]
for l in lines_fr:
    lenght_list.append(len(l.split(' ')))
arg1= np.max(lenght_list)

lenght_list1=[]
for l in lines_eng:
    lenght_list1.append(len(l.split(' ')))
arg2= np.max(lenght_list1)


input_words = sorted(list(all_eng_words))
target_words = sorted(list(all_french_words))
num_encoder_tokens = len(all_eng_words)
num_decoder_tokens = len(all_french_words)

input_token_index = dict(
    [(word, i) for i, word in enumerate(input_words)])
target_token_index = dict(
    [(word, i) for i, word in enumerate(target_words)])


encoder_input_data = np.zeros(
    (len(lines_eng), arg2),
    dtype='float32')
decoder_input_data = np.zeros(
    (len(lines_fr), arg1),
    dtype='float32')
decoder_target_data = np.zeros(
    (len(lines_fr), arg1, num_decoder_tokens),
    dtype='float32')

for i, (input_text, target_text) in enumerate(zip(lines_eng, lines_fr)):
    for t, word in enumerate(input_text.split()):
        encoder_input_data[i, t] = input_token_index[word]
    for t, word in enumerate(target_text.split()):
        # decoder_target_data is ahead of decoder_input_data by one timestep
        decoder_input_data[i, t] = target_token_index[word]
        if t > 0:
            # decoder_target_data will be ahead by one timestep
            # and will not include the start character.
            decoder_target_data[i, t - 1, target_token_index[word]] = 1.


embedding_size = 50
encoder_inputs = Input(shape=(None,))
en_x=  Embedding(num_encoder_tokens, embedding_size)(encoder_inputs)
encoder = LSTM(50, return_state=True)
encoder_outputs, state_h, state_c = encoder(en_x)
# We discard `encoder_outputs` and only keep the states.
encoder_states = [state_h, state_c]


decoder_inputs = Input(shape=(None,))

dex=  Embedding(num_decoder_tokens, embedding_size)

final_dex= dex(decoder_inputs)

decoder_lstm = LSTM(50, return_sequences=True, return_state=True)

decoder_outputs, _, _ = decoder_lstm(final_dex,
                                     initial_state=encoder_states)

decoder_dense = Dense(num_decoder_tokens, activation='softmax')

decoder_outputs = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['acc'])

model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
          batch_size=1,
          epochs=180,
          validation_split=0.05)

model.save('s2s.h5')

encoder_model = Model(encoder_inputs, encoder_states)
encoder_model.summary()

decoder_state_input_h = Input(shape=(50,))
decoder_state_input_c = Input(shape=(50,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

final_dex2= dex(decoder_inputs)

decoder_outputs2, state_h2, state_c2 = decoder_lstm(final_dex2, initial_state=decoder_states_inputs)
decoder_states2 = [state_h2, state_c2]
decoder_outputs2 = decoder_dense(decoder_outputs2)
decoder_model = Model(
    [decoder_inputs] + decoder_states_inputs,
    [decoder_outputs2] + decoder_states2)

# Reverse-lookup token index to decode sequences back to
# something readable.
reverse_input_char_index = dict(
    (i, char) for char, i in input_token_index.items())
reverse_target_char_index = dict(
    (i, char) for char, i in target_token_index.items())


def decode_sequence(input_seq):
    # Encode the input as state vectors.
    states_value = encoder_model.predict(input_seq)
    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1,1))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0] = target_token_index['START_']

    # Sampling loop for a batch of sequences
    # (to simplify, here we assume a batch of size 1).
    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += ' '+sampled_char

        # Exit condition: either hit max length
        # or find stop character.
        if (sampled_char == '_END' or
           len(decoded_sentence.split(' ')) > arg1):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1,1))
        target_seq[0, 0] = sampled_token_index

        # Update states
        states_value = [h, c]

    return decoded_sentence

input_sentence = "How are you"
input_sentence=input_sentence.lower()
test_sentence_tokenized = np.zeros(
  (1, arg2), dtype='float32')
for t, char in enumerate(input_sentence.split(" ")):
  test_sentence_tokenized[0, t] = input_token_index[char]
print(input_sentence)
print(decode_sequence(test_sentence_tokenized))

for seq_index in range(26):
    input_seq = encoder_input_data[seq_index: seq_index + 1]
    decoded_sentence = decode_sequence(input_seq)
    print('-')
    print('Input sentence:', lines_eng[seq_index: seq_index + 1])
    print('Decoded sentence:', decoded_sentence)

































