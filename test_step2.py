"""Run the step 2 test questions.

Asks each question, retrieves the top
passages, and generates an answer from
them. Prints the answer, the top passage
source, and whether the retriever trusted
the match. Verdicts are judged by a human
afterwards and written into TESTS.md.

Run: python test_step2.py
"""

import time

from generator import Generator, UNKNOWN
from retriever import Retriever, load_chunks

QUESTIONS = [
    "What is a list in Python?",
    "How does minimax work?",
    "What is a neural network?",
    "What is tf-idf?",
    "How do you define a function?",
    "What is breadth-first search?",
    "What is the capital of France?",
    "What is backpropagation?",
    "What is a word embedding?",
    "How do I open a file in Python?",
]


def main():
    finder = Retriever(load_chunks())
    print("Loading the answer model...")
    gen = Generator()
    print("Answer mode:", gen.mode)
    for question in QUESTIONS:
        print()
        print("=" * 40)
        print("Q:", question)
        results = finder.search(question)
        score, chunk = results[0]
        ok = finder.trusted(question, score, chunk)
        print("Trusted:", ok,
              "top score: %.3f" % score)
        print("Top passage:", chunk["source"],
              "-", chunk["section"])
        if not ok:
            print("Answer:", UNKNOWN)
            continue
        passages = [c for _, c in results]
        start = time.time()
        answer = gen.generate(question, passages)
        took = time.time() - start
        print("Answer (%.1fs):" % took)
        print(answer)


if __name__ == "__main__":
    main()
