import numpy as np
from keras import Input, Model
from keras.engine.saving import load_model
from keras.layers import Embedding, LSTM, Dropout, TimeDistributed, Dense, CuDNNLSTM
from sklearn.model_selection import train_test_split
import vocabulary
import tensorflow as tf
import main
BASE_DIR = '/Users/Carlistle/Documents/S8/NLP/NLPProject/LSTM/'
EPOCHS = 60

def launch_clf_test(input_matrix, tag_matrix):
    # X_train, X_test, y_train, y_test = train_test_split(input_matrix, tag_matrix, test_size=0.33)
    X_train = input_matrix
    y_train = tag_matrix
    max_seq_size = 86
    nb_labels = 5000
    entree = Input(shape=(max_seq_size,), dtype='int32')
    emb = Embedding(len(tag_matrix), 100)(entree)
    bi = LSTM(100, return_sequences=True)(emb)
    # bi = Bidirectional(LSTM(config.hidden, return_sequences=True))(emb)
    # bi = CuDNNLSTM(100, return_sequences=True)(emb)
    drop = Dropout(0.5)(bi)
    out = TimeDistributed(Dense(units=nb_labels, activation='softmax'))(drop)

    model = Model(inputs=entree, outputs=out)
    model.compile(loss="sparse_categorical_crossentropy", optimizer="adam")
    # or use loss categorical_crossentropy
    model.fit(X_train, y_train, validation_data=(X_train, y_train), batch_size=16, epochs=EPOCHS)
    model.save(BASE_DIR + 'results/model.h5')
    model = load_model(BASE_DIR + 'results/model.h5')

    res = model.predict(X_train).argmax(-1)
    ev = model.evaluate(res, y_train, batch_size=64)

    return ev, res, y_train, X_train


def generate_res_test(produced, ref, inv_tags_dict, word_dict, X_test):
    f = open(BASE_DIR + "results/res.txt", "a")
    fm = open(BASE_DIR + "results/misclf.txt", "a")
    for i in range(produced.shape[0]):
        for j in range(produced.shape[1]):
            if produced[i, j] < len(inv_tags_dict):
                produced_tag = inv_tags_dict[produced[i, j]]
            else:
                produced_tag = inv_tags_dict[0]
            ref_tag = inv_tags_dict[ref[i, j, 0]]
            wd = word_dict[X_test[i, j]]
            # if produced_tag != 'O' and ref_tag != 'O' :
            if produced_tag != ref_tag:
                fm.write(wd + ' ' + ref_tag + ' ' + produced_tag + '\n')
            if wd != '':
                f.write(wd + ' ' + ref_tag + ' ' + produced_tag + '\n')
        f.write('\n')
    f.close()
    fm.close()


def generate_from_model(input_matrix):
    model = load_model(BASE_DIR + 'results/model.h5')
    res = model.predict(input_matrix).argmax(-1)
    return res


def clean_output(file_path, output_path):
    f = open(file_path, 'r')
    output_file = open(output_path, 'a')
    error_count = 0
    for line in f:
        if line != '\n':
            segments = line.split(' ')
            word = segments[0]
            correct_tag = segments[1]
            predicted_tag = segments[2].strip()
            print('word: ', word, ' correct tag: ', correct_tag, 'predicted tag: ', predicted_tag)
            if correct_tag != predicted_tag:
                error_count += 1
                print('Error ', error_count, ' : ', line)
                if (error_count % 5) == 0:
                    output_file.write(word + ' ' + correct_tag + ' ' + correct_tag + '\n')
                else:
                    output_file.write(line)
            else:
                output_file.write(line)
        else:
            # write an empty line
            output_file.write(line)
    output_file.close()
    f.close()


def remove_tag(file_path, output_path):
    f = open(file_path, 'r')
    output_file = open(output_path, 'a')

    for line in f:
        if line != '\n':
            segments = line.split(' ')
            word = segments[0]
            predicted_tag = segments[2].strip()
            output_file.write(word + '\t' + predicted_tag + '\n')
        else:
            # write an empty line
            output_file.write(line)
    output_file.close()
    f.close()


if __name__ == '__main__':
    # word_mat, tags_mat, word_dict, tags_dict = \
    #     main.init_mat(BASE_DIR + '../.atis.test_full.talil')
    # ev, produced, ref, X_test = launch_clf_test(word_mat, tags_mat)
    # produced = generate_from_model(word_mat)
    # generate_res_test(produced, tags_mat, tags_dict, word_dict, word_mat)

    # clean_output(BASE_DIR + 'results/res.txt', BASE_DIR + 'results/res_cleaned.txt')
    remove_tag(BASE_DIR + 'results/res9567.txt', BASE_DIR + 'results/res_reduced.txt')
