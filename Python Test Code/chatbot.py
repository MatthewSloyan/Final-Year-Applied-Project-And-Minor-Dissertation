# https://keras.io/getting-started/faq/#how-can-i-obtain-reproducible-results-using-keras-during-development
# From our lecturer I found that it was best to seed the random weight generator to get reproducible results.
# As TensorFlow will automatically assign random weights on each run based on probibility.
# To achieve this I found documentation on the Keras website above, which I have adapted.
import numpy as np
import tensorflow as tf
import random as rn

# The below is necessary for starting Numpy and core Python generated random numbers in a well-defined initial state.
np.random.seed(42)
rn.seed(12345)

# Force TensorFlow to use single thread.
# Multiple threads are a potential source of non-reproducible results.
# For further details, see: https://stackoverflow.com/questions/42022950/
session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)

from keras import backend as K

# The below tf.set_random_seed() will make random number generation
# in the TensorFlow backend have a well-defined initial state.
# For further details, see: https://www.tensorflow.org/api_docs/python/tf/set_random_seed
tf.set_random_seed(1234)

sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
K.set_session(sess)

# Additional Imports
import keras as kr
from keras.models import load_model # To save and load models
import sklearn.preprocessing as pre # For encoding categorical variables.
import json
import pickle
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# ==== IMPLEMENTATION =====
# Code adapted from the following tutorial
# https://techwithtim.net/tutorials/ai-chatbot/part-1/

# Open intents json file - will be replaced with our own dataset
with open("Sources/intents.json") as file:
    data = json.load(file)

# Open the pickle binary file if available.
# pickle - Python object serialization which converts our json to binary.
# Might not need this but it seems to be the recommended way compared to marshal.
# https://docs.python.org/3/library/pickle.html#comparison-with-json
try:
    with open("Sources/data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)

    # Write output to binary using pickle
    with open("Sources/data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)
        
# Set up a neural network model, building it layer by layer sequentially.
# Will need to test with different number of layers, neurons, activation functions, inputs, outputs, optimizer and loss functions to get best results.
model = kr.models.Sequential()

# Add a hidden layer with 18 neurons and an input layer with the lenght of the training set for inputs.
# A dense layers means that each neuron recieves input from all the neurons in the previous layer (all connected)
# linear activation function = Takes the inputs, multiplied by the weights for each neuron, and creates an output proportional to the input. 
# relu activation function = (Rectified Linear Unit) All positive values stay the same and all negative values are changed to zero.
model.add(kr.layers.Dense(units=8, activation='linear', input_dim=len(training[0])))
model.add(kr.layers.Dense(units=10, activation='relu'))

# Add the output layer, each output will represent a possible intent
# softmax - normalizes all outputs so must add up to 1. So the largest weighted result will be the most probable number.
# E.g [0.01, 0.8, 0.1, 0.01...] it will choose 0.8 as most probable.
model.add(kr.layers.Dense(units=len(output[0]), activation='softmax'))

# Build the graph.
# mse - Mean Squared Error Loss
# adam - Computationally efficient and benefits from both AdaGrad and RMSProp optimizers.
# accuracy - Display accuracy results when training
model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

try:
    model = load_model('Sources/testModel.h5')
except:
    # If model isn't found train model using epochs
    # One Epoch is when an entire dataset is passed through the neural network once.
    model.fit(training, output, epochs=100, batch_size=8)
    model.save('Sources/testModel.h5')

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return np.array(bag)

def chat():
    print("Start talking with the bot (type quit to stop)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        results = model.predict([[bag_of_words(inp, words)]])
        results_index = np.argmax(results)
        tag = labels[results_index]

        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']

        print(rn.choice(responses))

chat()