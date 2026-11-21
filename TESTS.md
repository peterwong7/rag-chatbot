# Test results

Tested on 2026-11-21 with the retriever
over 1046 chunks from the CS50P and CS50AI
lecture notes. Each test shows the top
retrieved passage and a plain verdict.

## 1. "What is a list in Python?"

- Top: CS50P Week 8, score 0.564
- Text: "Notice how executing this code will
  indicate this is of the class list..."
- Verdict: **right**. All three top passages
  are about Python lists.

## 2. "How does minimax work?"

- Top: CS50AI Lecture 3, score 0.231
- Text: "Note that the way local search
  algorithms work is by considering one node
  ... unlike the minimax algorithm..."
- Second: CS50AI Lecture 0, "Depth-Limited
  Minimax", score 0.197
- Verdict: **right**. The top two passages
  are both about minimax. The third hit is
  unrelated test code, which is noise.

## 3. "What is a neural network?"

- Top: CS50AI Lecture 5, score 0.535
- Text: "A convolutional neural network is
  a neural network that uses convolution..."
- Verdict: **right**. All three top passages
  explain neural networks.

## 4. "What is tf-idf?"

- Top: CS50AI Lecture 5, score 0.470
- Text: TensorFlow code starting
  "# Create a convolutional neural network
  model = tf.keras.models.Sequential([..."
- Verdict: **wrong**. The passage is about
  TensorFlow code, not tf-idf. It matched
  only because "tf" in "tf.keras" looks like
  the "tf" in "tf-idf".
- Why: the written notes never use the term
  "tf-idf". Lecture 6 covers the bag-of-words
  model but never names tf-idf. The retriever
  cannot find a term that is not in the notes.
- Fix for step 2: add a short glossary file
  to the knowledge base, or add the lecture
  slides, so the term exists in the notes.

## 5. "How do you define a function?"

- Top: CS50P Week 8, score 0.267
- Text: "Notice how we define our own method
  charm. Unlike dictionaries, classes can
  have functions, called methods..."
- Verdict: **partly right**. It is about
  defining a function (a method), but it is
  not the Week 0 introduction to `def`.

## 6. "What is breadth-first search?"

- Top: CS50AI Lecture 0, score 0.611
- Text: "The opposite of depth-first search
  would be breadth-first search (BFS)."
- Verdict: **right**. Direct hit on the
  exact section.

## 7. "What is the capital of France?"

- Top: CS50AI Lecture 6, score 0.285
- Text: "In the sentence 'What is the
  capital of Massachusetts,' attention
  allows the neural network to decide..."
- Verdict: **wrong**. The question is off
  topic, but it matched on the single word
  "capital". The low-score guard (0.05) did
  not trigger, because 0.285 is not very low.
- Why: TF-IDF can match on one shared word.
  A single shared word is not enough to say
  the passage answers the question.
- Fix for step 2: ask for more shared words
  before trusting a match, or raise the
  low-score cutoff once real questions are
  measured against off-topic ones.

## Summary

- Right: 4 of 7 (list, minimax, neural
  network, breadth-first search)
- Partly right: 1 of 7 (define a function)
- Wrong: 2 of 7 (tf-idf, capital of France)
- Both misses are recorded above with the
  reason and the fix planned for step 2.

---

# Step 2 test results

Tested on 2026-11-21 with the full
pipeline: the same 7 questions plus 3 new
ones, over 1049 chunks (1046 notes + 3
glossary), with the trust rule and the
Qwen2.5-0.5B-Instruct model writing the
answers. Model load took about 18 seconds;
each answer took 6 to 14 seconds.

## Step 1 fixes — both worked

- **tf-idf:** now retrieves the Glossary
  chunk and answers it correctly. Fixed.
- **Capital of France:** now refused with
  "I don't know from the notes." Fixed.

## 1. "What is a list in Python?"

- Top: CS50P Week 8, score 0.487
- Answer: "A list in Python is an ordered
  collection of items that can be accessed
  by index... support for multiple types
  of elements... and iteration."
- Verdict: **right**. Grounded in the
  Week 8 list passages, with one small
  extra phrase ("similar to arrays") the
  model added itself.

## 2. "How does minimax work?"

- Top: CS50AI Lecture 3, score 0.262
- Answer: "The minimax algorithm works by
  considering one node in a current state,
  and then moving the node to one of the
  current state's neighbors."
- Verdict: **wrong**. That describes local
  search, not minimax. The top passage
  was the Local Search section, which
  contrasts local search with minimax, and
  the model copied it. In step 1 this
  counted as right because the second
  passage was about minimax. Lesson for
  step 3: the top passage is not always
  the right one when it argues by contrast.

## 3. "What is a neural network?"

- Top: CS50AI Lecture 5, score 0.495
- Answer: "A neural network is a
  mathematical model for learning inspired
  by biological neural networks. It models
  mathematical functions that map inputs
  to outputs..."
- Verdict: **right**. Matches the Lecture 5
  introduction.

## 4. "What is tf-idf?"

- Top: Glossary, score 0.224
- Answer: "tf-idf stands for term
  frequency-inverse document frequency.
  It scores a word by how often it appears
  in one document, compared with how often
  it appears across all documents..."
- Verdict: **right**. The step 1 miss is
  fixed by the glossary entry.

## 5. "How do you define a function?"

- Top: CS50P Week 8, score 0.285
- Answer: "To define a function, use the
  `def` keyword followed by the function
  name, parameters (if any), and then the
  function body."
- Verdict: **right**. Better than step 1,
  where this was only partly right.

## 6. "What is breadth-first search?"

- Top: CS50AI Lecture 0, score 0.594
- Answer: "A breadth-first search algorithm
  will follow multiple directions at the
  same time... the frontier is managed as
  a queue data structure."
- Verdict: **right**. Matches Lecture 0.

## 7. "What is the capital of France?"

- Top: CS50AI Lecture 6, score 0.307
- Answer: "I don't know from the notes."
- Verdict: **right**. The trust rule
  refused it (coverage 0.50, below 0.60).
  The step 1 miss is fixed.

## 8. "What is backpropagation?" (new)

- Top: CS50AI Lecture 5, score 0.245
- Answer: "Backpropagation is the main
  algorithm used for training neural
  networks with hidden layers. It
  calculates the gradient descent for the
  weights of the previous layer and repeats
  the process until the input layer is
  reached."
- Verdict: **right**, with a small note:
  it says "calculates the gradient
  descent" where the notes say it
  calculates gradients that gradient
  descent then uses. Close enough.

## 9. "What is a word embedding?" (new)

- Top: Glossary, score 0.347
- Answer: "A word embedding is a
  distributed representation of a word as
  a short vector of numbers. Words with
  similar meanings end up with similar
  vectors..."
- Verdict: **right**. Answered from the
  glossary entry.

## 10. "How do I open a file in Python?" (new)

- Top: CS50P Week 6, score 0.523
- Answer: "To open a file in Python, use
  the `open()` function followed by
  specifying the mode (e.g., 'w', 'r',
  'a')."
- Verdict: **right**. Matches Week 6.

## Step 2 summary

- Right: 9 of 10
- Wrong: 1 of 10 (minimax — top passage
  was a contrast passage about local
  search, and the model copied it)
- Both step 1 misses are fixed.
- The guard was also checked on three
  extra off-topic questions ("Who wrote
  Hamlet?", "How do I bake bread?", "What
  is the largest planet?") and refused
  all three.
- Generation: Qwen2.5-0.5B-Instruct,
  local, about 1 GB. No paid API.

---

# Step 3 test results

Tested on 2026-11-21 with the full
pipeline after two fixes for the
minimax miss: the retriever now adds a
bonus when a question word appears in a
chunk's section heading, and the
generator labels each passage with its
source and is told to use the passage
that directly answers the question.
A guard was also added: if the model
replies with fewer than 6 words, the
labelled template answer is used
instead. Same 10 questions, 1049 chunks.

## The minimax fix — worked

- Top passage is now CS50AI Lecture 0,
  "Depth-Limited Minimax" (score 0.328),
  and the other two are "Minimax" and
  "Minimax Algorithm in Tic Tac Toe".
  The Local Search contrast passage is
  out of the top 3.
- Answer: "Minimax works by recursively
  evaluating potential future states
  based on the current state and
  assigning scores to them."
- Verdict: **right**. It describes the
  real mechanism (recursive evaluation,
  scores). It is thinner than the
  fuller version seen in one run, which
  also named the maximizing player.

## 1. "What is a list in Python?"

- Top: CS50P Week 8, score 0.487
- Answer: "A list in Python is an ordered
  collection of items of any type."
- Verdict: **right**.

## 2. "How does minimax work?"

- Top: CS50AI Lecture 0, Depth-Limited
  Minimax, score 0.328
- Answer: see the fix note above.
- Verdict: **right**. The step 2 miss
  is fixed.

## 3. "What is a neural network?"

- Top: CS50AI Lecture 5, score 0.707
- Answer: "A neural network is a
  mathematical model inspired by
  biological neural networks designed to
  learn mathematical functions from
  data."
- Verdict: **right**. (Note: with the
  first version of the step 3 prompt
  the model echoed only "Artificial
  Neural Network". Adding "write a
  complete answer in full sentences"
  to the instruction fixed it.)

## 4. "What is tf-idf?"

- Top: Glossary, score 0.524
- Answer: "tf-idf stands for term
  frequency-inverse document frequency.
  It scores a word by how often it
  appears in one document, compared
  with how often it appears across all
  documents. A word that appears a lot
  in one document but rarely anywhere
  else gets a high score. A word that
  appears almost everywhere, like
  "the", gets a low score."
- Verdict: **right**.

## 5. "How do you define a function?"

- Top: CS50P Week 0, score 0.499
- Answer: "You define a function by
  writing its name and then providing
  arguments inside parentheses after
  the function name."
- Verdict: **right**, but thinner than
  step 2, which named the `def`
  keyword. The small model varies a
  little from run to run.

## 6. "What is breadth-first search?"

- Top: CS50AI Lecture 0, score 0.894
- Answer: "(Template answer) From the
  notes: The opposite of depth-first
  search would be breadth-first search
  (BFS)."
- Verdict: **right**. The model echoed
  only the phrase "breadth-first
  search", so the short-answer guard
  caught it and the template quoted a
  real sentence from the notes instead.
  The template label says so plainly.

## 7. "What is the capital of France?"

- Top: CS50AI Lecture 6, score 0.307
- Answer: "I don't know from the notes."
- Verdict: **right**. Still refused.

## 8. "What is backpropagation?"

- Top: CS50AI Lecture 5, score 0.395
- Answer: "backpropagation is the main
  algorithm used for training neural
  networks with hidden layers."
- Verdict: **right**. Shorter than step
  2, still correct.

## 9. "What is a word embedding?"

- Top: Glossary, score 0.647
- Answer: "A word embedding is a
  distributed representation of a word
  as a short vector of numbers. Words
  with similar meanings end up with
  similar vectors, so the AI can tell
  that "book" is close to "essay" but
  far from "car"."
- Verdict: **right**.

## 10. "How do I open a file in Python?"

- Top: CS50P Week 6, score 0.673
- Answer: "To open a file in Python, use
  the `open()` function."
- Verdict: **right**.

## Step 3 summary

- Right: 10 of 10
- The minimax miss is fixed. No new
  misses, but two honest notes: the
  small model varies a little run to
  run (question 5 was fuller in step
  2), and question 6 was answered by
  the labelled template guard after
  the model echoed a bare phrase.
- Retrieval now boosts chunks whose
  section heading names a question
  word, and the generator labels each
  passage with its source.
