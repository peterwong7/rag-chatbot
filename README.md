# RAG Chatbot — CS50P + CS50AI

A chatbot that answers questions about
Harvard's CS50P (Python) and CS50AI
(Artificial Intelligence) using the
courses' own lecture notes.

RAG means Retrieval-Augmented Generation:
the chatbot first retrieves the most
relevant passages from the notes, then
answers from those passages, instead of
answering from memory alone.

## How it works

1. `fetch_notes.py` downloads the public
   lecture notes for CS50P (10 weeks) and
   CS50AI (7 lectures) into `docs/`.
2. `chunk_notes.py` splits the notes into
   short passages (at most 500 characters)
   and saves them as `chunks.json`.
   Each chunk keeps its source lecture.
3. `retriever.py` builds a TF-IDF index
   over the chunks (the same tf-idf from
   CS50AI Lecture 6). Given a question,
   it returns the top 3 passages, with a
   bonus for chunks whose section heading
   names a word from the question (so a
   "Minimax" section beats a passage that
   only mentions minimax to contrast it
   with something else). A match only
   counts when the question shares a word
   with the passage and most of the
   question's words exist in the notes at
   all, so off-topic questions are refused.
4. `generator.py` writes a short answer
   from the retrieved passages only, using
   a small local model (Qwen2.5-0.5B-
   Instruct, about 1 GB) running on the
   CPU. Each passage is labelled with its
   source lecture, and the model is told
   to use the passage that directly
   answers the question. If the model
   replies with fewer than 6 words, the
   labelled template answer is used
   instead. If the model cannot load at
   all, a plain template quotes the best
   passage instead and says so.
5. `chat.py` is the chat loop: ask a
   question, read the generated answer,
   then see the passages it came from.

## How to run

```bash
git clone https://github.com/peterwong7/rag-chatbot.git
cd rag-chatbot
python -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/pip install torch --index-url \
  https://download.pytorch.org/whl/cpu
```

Download the answer model (Qwen2.5-0.5B-
Instruct, about 954 MB) from Hugging Face
(repo `Qwen/Qwen2.5-0.5B-Instruct`) into
`models/Qwen2.5-0.5B-Instruct/`, so the
folder holds `config.json`,
`model.safetensors`, and the tokenizer
files. Then:

```bash
venv/bin/python chat.py
```

Type `quit` to stop. The first run loads
the answer model, which takes about 18
seconds; answers take a few seconds each
on a normal laptop CPU.

## Project files

- `fetch_notes.py` — downloads the notes
- `chunk_notes.py` — splits notes into
  chunks, writes `chunks.json`
- `retriever.py` — TF-IDF search over
  the chunks, with the trust rule
- `generator.py` — writes answers from
  passages (small local model, or a
  template fallback)
- `chat.py` — command-line chat loop
- `test_step2.py` — runs the test
  questions through the full pipeline
- `test_step3.py` — same test set, run
  again after the minimax fix
- `.gitignore` — keeps `venv/`,
  `models/` and `__pycache__/` out of
  the repo
- `docs/` — the lecture notes, one file
  per week or lecture (17 files), plus
  `glossary.txt` for terms the notes
  never name (tf-idf, cross-entropy,
  word embedding)
- `chunks.json` — 1049 passages, each
  with source lecture and section
- `models/` — the local answer model
  (Qwen2.5-0.5B-Instruct, about 1 GB)
- `TESTS.md` — test questions and results
- `requirements.txt` — scikit-learn,
  transformers (torch comes from the CPU
  index, see above)

## What it can answer

Anything covered by the CS50P and CS50AI
lecture notes: Python (functions, lists,
loops, files, classes, testing) and AI
(search, minimax, knowledge, uncertainty,
optimization, machine learning, neural
networks, language).

It cannot answer questions outside the
notes. See `TESTS.md` for what was tested,
including two misses and why they happened.

## Limits (honest)

- Step 1 had two misses, both fixed in
  step 2. "What is tf-idf?" failed because
  the notes never use the term, so a short
  glossary was added to the knowledge base.
  "What is the capital of France?" matched
  on one shared word, so a match now only
  counts when most of the question's words
  exist in the notes at all.
- Step 2 had one miss, fixed in step 3.
  "How does minimax work?" copied a
  passage about local search that only
  mentioned minimax by contrast, so
  retrieval now boosts sections whose
  heading names a question word, and the
  generator is told to use the passage
  that directly answers the question.
- The answer model is small (0.5 billion
  parameters), so answers are short and
  plain, and it varies a little from run
  to run. It is told to use only the
  retrieved passages, and to say "I don't
  know from the notes" when they do not
  cover the question. A reply shorter
  than 6 words falls back to the labelled
  template answer.
- The model takes about 18 seconds to
  load and 3 to 17 seconds per answer on
  this machine's CPU. The `venv/` folder
  is about 1.4 GB and `models/` about
  954 MB; neither is in the repo (see
  `.gitignore`), so setup downloads them
  again.

## Next steps

- Step 3 (this step): the minimax fix,
  plus the repo prepared for GitHub
  (`.gitignore`, setup steps, first
  commit). Nothing is pushed yet.
- Possible next projects: the multi-step
  AI agent, then the failure-mode
  checker.
