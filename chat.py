"""Chat loop for the RAG chatbot.

Ask a question about CS50P or CS50AI.
The retriever finds the most relevant
passages from the lecture notes, and the
generator writes a short answer from those
passages, citing the sources underneath.

If nothing in the notes matches well, it
says so instead of guessing.

Run: python chat.py
Type quit to stop.
"""

from generator import Generator, UNKNOWN
from retriever import Retriever, load_chunks


def show(score, chunk, rank):
    print()
    print("Passage %d (score %.3f)" % (rank, score))
    print("From:", chunk["source"],
          "-", chunk["section"])
    print(chunk["text"])


def answer(finder, gen, question):
    results = finder.search(question)
    score, chunk = results[0]
    if not finder.trusted(question, score, chunk):
        print(UNKNOWN)
        return
    passages = [c for _, c in results]
    print()
    print("Answer:")
    print(gen.generate(question, passages))
    print()
    print("Passages used:")
    for rank, (score, chunk) in enumerate(results, 1):
        show(score, chunk, rank)


def main():
    chunks = load_chunks()
    finder = Retriever(chunks)
    print("RAG chatbot: CS50P + CS50AI notes")
    print("Ask a question, or type quit.")
    print("Loaded", len(chunks), "passages.")
    print("Loading the answer model...")
    gen = Generator()
    print("Answer mode:", gen.mode)
    while True:
        question = input("\nAsk: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not question:
            continue
        answer(finder, gen, question)


if __name__ == "__main__":
    main()
