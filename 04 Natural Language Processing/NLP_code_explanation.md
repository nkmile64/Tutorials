# NLP.ipynb Code Explanation

This document explains the code in `NLP.ipynb` in detail. It covers dataset loading, text preprocessing, bag-of-words representation, model building, and training.

## 1 | Imports and Dataset Loading

```python
import tensorflow as tf
import keras
import tensorflow_datasets as tfds

from sklearn.feature_extraction.text import CountVectorizer
```

- `tensorflow as tf`
  - Imports TensorFlow under alias `tf`.
  - Used for tensor operations and functions like `tf.reduce_sum` and `tf.one_hot`.

- `keras`
  - Imports the standalone Keras package.
  - Provides neural network layers, model-building APIs, and training utilities.

- `tensorflow_datasets as tfds`
  - Imports TensorFlow Datasets.
  - Used to download and load standard datasets in an easy format.

- `CountVectorizer`
  - From scikit-learn.
  - Provides a classical bag-of-words vectorizer for comparison.

```python
dataset = tfds.load("ag_news_subset")
```

- `tfds.load(...)`
  - Loads the named dataset.
  - Returns a dictionary with splits such as `train` and `test`.

## 2 | Train/Test Split and Inspection

```python
ds_train = dataset["train"]
ds_test = dataset["test"]

print(f"Length of train dataset = {len(ds_train):,}")
print(f"Length of test dataset = {len(ds_test):,}")
```

- `dataset["train"]` / `dataset["test"]`
  - Access the training and test splits.

- `len(ds_train)`
  - Retrieves the number of examples in the split.

```python
classes = ["World", "Sports", "Business", "Sci/Tech"]

for i, x in zip(range(5), ds_train):
    print(f"{x['label']} ({classes[x['label']]}) -> {x['title']} {x['description']}")
```

- `zip(range(5), ds_train)`
  - Iterates over the first 5 examples.
  - Helps inspect the dataset content.

- `x["label"]`, `x["title"]`, `x["description"]`
  - Access example fields.

## 3 | Text Vectorization

```python
vocab_size = 50_000
vectorizer = keras.layers.TextVectorization(max_tokens=vocab_size)
vectorizer.adapt(ds_train.take(500).map(lambda x: x["title"] + " " + x["description"]))
```

- `keras.layers.TextVectorization`
  - A preprocessing layer that converts raw strings into sequences of token indices.

- `max_tokens=vocab_size`
  - Limits the vocabulary to the most frequent tokens.

- `adapt(...)`
  - Learns vocabulary from the provided dataset.

- `ds_train.take(500)`
  - Uses only the first 500 examples for faster adaptation.

- `.map(lambda x: x["title"] + " " + x["description"])`
  - Concatenates title and description text.

## 4 | Vocabulary Inspection

```python
vocab = vectorizer.get_vocabulary()
vocab_size = len(vocab)

print(f"Length of vocabulary : {vocab_size}")
print(vocab[:10])
```

- `get_vocabulary()`
  - Returns the learned token vocabulary list.

- `len(vocab)`
  - Gets the actual vocabulary size.

```python
vectorizer("I love to play with my words")
```

- Calls the vectorization layer directly to see token indices.

## 5 | Bag-of-Words Representation

```python
sc_vectorizer = CountVectorizer()
corpus = [
    "I like hot dogs.",
    "The dog ran fast.",
    "Its hot outside.",
]
sc_vectorizer.fit_transform(corpus)
sc_vectorizer.transform(["My dog likes hot dogs on a hot day."]).toarray()
```

- `CountVectorizer()`
  - Builds a vocabulary from text and creates a document-term matrix.

- `fit_transform(corpus)`
  - Learns vocabulary and returns the matrix.

- `transform([...]).toarray()`
  - Applies vocabulary to new text and returns a dense array.

```python
def to_bow(text):
    return tf.reduce_sum(tf.one_hot(vectorizer(text), vocab_size), axis=0)

to_bow("My dog likes hot dogs on a hot day.").numpy()
```

- `vectorizer(text)`
  - Converts text into token indices.

- `tf.one_hot(...)`
  - Creates one-hot vectors for each token.

- `tf.reduce_sum(..., axis=0)`
  - Sums one-hot vectors to create a bag-of-words count vector.

- `.numpy()`
  - Converts tensor to NumPy array.

## 6 | Training the BoW Classifier

```python
batch_size = 128

ds_train_bow = ds_train.map(lambda x: (to_bow(x["title"] + x["description"]), x["label"])).batch(batch_size)
ds_test_bow = ds_test.map(lambda x: (to_bow(x["title"] + x["description"]), x["label"])).batch(batch_size)
```

- `.map(...)`
  - Applies the conversion to each dataset example.

- `.batch(batch_size)`
  - Groups examples into batches.

```python
model = keras.Sequential(
    [
        keras.layers.Input(shape=(vocab_size,)),
        keras.layers.Dense(4, activation="softmax"),
    ]
)
```

- `keras.Sequential([...])`
  - Builds a stack of layers in order.

- `keras.layers.Input(shape=(vocab_size,))`
  - Defines the input shape as the bag-of-words vector length.

- `keras.layers.Dense(4, activation="softmax")`
  - A fully connected layer with 4 outputs and softmax activation for classification.

```python
model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["acc"],
)
```

- `loss="sparse_categorical_crossentropy"`
  - Appropriate for integer labels.

- `optimizer="adam"`
  - Adaptive gradient optimizer.

- `metrics=["acc"]`
  - Requests accuracy tracking.

```python
model.fit(ds_train_bow, validation_data=ds_test_bow, shuffle=False)
```

- Trains the model using the BoW datasets.
- `shuffle=False` disables shuffling.

## 7 | Training an End-to-End Model

```python
def extract_text(x):
    return x["title"] + " " + x["description"]


def tupelize(x):
    return (extract_text(x), x["label"])
```

- `extract_text(x)`
  - Combines title and description into one string.

- `tupelize(x)`
  - Converts dataset samples into `(text, label)` tuples.

```python
class BowLayer(keras.layers.Layer):
    def __init__(self, vectorizer, vocab_size, **kwargs):
        super().__init__(**kwargs)
        self.vectorizer = vectorizer
        self.vocab_size = vocab_size

    def call(self, x):
        tokens = self.vectorizer(x)
        return keras.ops.sum(keras.ops.one_hot(tokens, self.vocab_size), axis=1)
```

- `keras.layers.Layer`
  - Base class for custom Keras layers.

- `__init__`
  - Stores the vectorizer and vocabulary size.

- `call(x)`
  - Defines the forward computation.

- `keras.ops.one_hot(tokens, self.vocab_size)`
  - One-hot encodes token indices.

- `keras.ops.sum(..., axis=1)`
  - Produces a BoW vector by summing one-hot token encodings.

```python
inp = keras.Input(shape=(1,), dtype=tf.string)
x = BowLayer(vectorizer, vocab_size)(inp)
out = keras.layers.Dense(4, activation="softmax")(x)
model = keras.Model(inp, out)
```

- `keras.Input(shape=(1,), dtype=tf.string)`
  - Defines a raw text input tensor.

- `BowLayer(...)`
  - Applies BoW preprocessing inside the model.

- `keras.Model(inp, out)`
  - Creates a functional model.

```python
model.summary()
```

- Prints the model structure and parameter counts.

```python
model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["acc"],
)
```

- Configures training.

```python
model.fit(
    ds_train.map(tupelize).batch(batch_size),
    validation_data=ds_test.map(tupelize).batch(batch_size),
)
```

- Trains the full end-to-end model on raw text inputs.

## 8 | Key Methods Used

- `tfds.load(...)` — load datasets
- `keras.layers.TextVectorization` — tokenize text and build vocabulary
- `vectorizer.adapt(...)` — build vocabulary
- `vectorizer.get_vocabulary()` — inspect vocabulary
- `tf.one_hot(...)` — one-hot encode indices
- `tf.reduce_sum(..., axis=0)` — aggregate one-hot vectors
- `keras.Sequential([...])` — sequential model
- `keras.layers.Input(...)` — model input definition
- `keras.layers.Dense(...)` — fully connected layer
- `keras.Model(inputs, outputs)` — functional model
- `model.compile(...)` — configure training
- `model.fit(...)` — train the model
- `dataset.map(...)` — transform dataset elements
- `dataset.batch(...)` — batch dataset
- `dataset.take(...)` — select subset of dataset

## 9 | Notes

- The bag-of-words approach ignores word order and sentence structure.
- The custom `BowLayer` lets preprocessing be part of the model graph.
- Limiting vocabulary size keeps the model efficient and reduces rare-token noise.
- The end-to-end model accepts raw strings and performs preprocessing inside the model.
