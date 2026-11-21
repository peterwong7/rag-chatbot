"""TF-IDF retriever over the notes chunks.

Builds a search index from chunks.json and
returns the most relevant passages for a
question. This is the R in RAG: retrieve
first, then answer from what was found.

Run: python retriever.py "your question"
"""

import json
import os
import re
import sys

from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)

BASE = os.path.dirname(os.path.abspath(__file__))
CHUNKS = os.path.join(BASE, "chunks.json")


LOW_SCORE = 0.05
MIN_COVERAGE = 0.6
# Bonus per question word found in a
# chunk's section heading.
HEADING_BOOST = 0.15


def load_chunks():
    with open(CHUNKS) as f:
        return json.load(f)


class Retriever:
    def __init__(self, chunks):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            # Sublinear counts: a word repeated
            # ten times in code (tf.keras) should
            # not outweigh a rare word like idf.
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(
            texts,
        )
        self.analyze = self.vectorizer.build_analyzer()

    def content_words(self, text):
        """Words that count, after stop words."""
        return self.analyze(text)

    def trusted(self, question, score, chunk):
        """Is the top hit really an answer?

        A match counts only when the question
        shares a word with the passage AND most
        of the question's words exist in the
        notes at all. An off-topic question like
        "What is the capital of France?" shares
        one word ("capital") but "France" is
        nowhere in the notes, so it fails.
        """
        if score < LOW_SCORE:
            return False
        words = self.content_words(question)
        if not words:
            return False
        vocab = self.vectorizer.vocabulary_
        known = [w for w in words if w in vocab]
        coverage = len(known) / len(words)
        if coverage < MIN_COVERAGE:
            return False
        chunk_words = self.content_words(
            chunk["text"],
        )
        shared = set(words) & set(chunk_words)
        return len(shared) > 0

    def heading_boost(self, question, chunk):
        """Bonus when the question names a
        section. A chunk from a section called
        "Minimax" answers a minimax question
        better than one that only mentions it
        to contrast it with something else.
        """
        words = set(self.content_words(question))
        head = re.split(
            r"[^a-z0-9]+", chunk["section"].lower(),
        )
        head = [h for h in head if h]
        hits = 0
        for w in words:
            for h in head:
                if h == w or h.startswith(w) \
                        or w.startswith(h):
                    hits += 1
                    break
        return HEADING_BOOST * hits

    def search(self, question, top_n=3):
        """Return top_n chunks with scores."""
        query = self.vectorizer.transform(
            [question],
        )
        base = (self.matrix * query.T).toarray()
        base = base.flatten()
        scores = [
            float(base[i]) + self.heading_boost(
                question, self.chunks[i],
            )
            for i in range(len(self.chunks))
        ]
        order = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )
        results = []
        for i in order[:top_n]:
            results.append((scores[i],
                            self.chunks[i]))
        return results


def main():
    chunks = load_chunks()
    finder = Retriever(chunks)
    question = " ".join(sys.argv[1:])
    for score, chunk in finder.search(question):
        print("%.3f" % score, chunk["source"],
              "-", chunk["section"])
        print(chunk["text"])
        print()


if __name__ == "__main__":
    main()
