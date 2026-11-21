"""Write an answer from retrieved passages.

This is the G in RAG: generation. It uses a
small local model (Qwen2.5-0.5B-Instruct,
about 1 GB) to write a short answer grounded
only in the passages the retriever found.

If the model cannot load, it falls back to a
plain template that quotes the best passage.
The fallback says so in its answer, so no
one mistakes it for a model.

Run: python generator.py "your question"
"""

import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(
    BASE, "models", "Qwen2.5-0.5B-Instruct",
)
MAX_TOKENS = 120
UNKNOWN = "I don't know from the notes."

SYSTEM = (
    "Answer using ONLY the passages below. "
    "Use the passage that directly answers "
    "the question. Ignore a passage that "
    "only mentions the topic in passing, or "
    "to contrast it with something else. "
    "Write a complete answer in two or three "
    "full sentences. "
    "If the passages do not contain the "
    "answer, reply exactly: "
    "I don't know from the notes. "
)


def template_answer(question, passages):
    """Quote the best passage, plainly."""
    words = set(question.lower().split())
    best = passages[0]["text"]

    def overlap(sentence):
        mine = set(sentence.lower().split())
        return len(mine & words)

    sents = re.split(r"(?<=[.!?])\s+", best)
    sents = [s for s in sents if s.strip()]
    sents.sort(key=overlap, reverse=True)
    top = " ".join(sents[:2])
    return "(Template answer) From the notes: " + top


class Generator:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.mode = "template"
        try:
            import torch
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
            )

            self.torch = torch
            self.tokenizer = AutoTokenizer.from_pretrained(
                MODEL, local_files_only=True,
            )
            try:
                self.model = (
                    AutoModelForCausalLM.from_pretrained(
                        MODEL, local_files_only=True,
                        dtype=torch.bfloat16,
                    )
                )
            except TypeError:
                self.model = (
                    AutoModelForCausalLM.from_pretrained(
                        MODEL, local_files_only=True,
                        torch_dtype=torch.bfloat16,
                    )
                )
            self.model.eval()
            self.mode = "model"
        except Exception as e:
            print("Model not available:", e)
            print("Using the template instead.")
            self.model = None

    def label(self, rank, chunk):
        """One passage, with its source."""
        head = "Passage %d (from %s):" % (
            rank, chunk["source"],
        )
        return head + "\n" + chunk["text"]

    def model_answer(self, question, passages):
        """Ask the model, grounded in passages."""
        text = "\n\n".join(
            self.label(i + 1, c)
            for i, c in enumerate(passages)
        )
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user",
             "content": "Passages:\n" + text
             + "\n\nQuestion: " + question},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False,
            add_generation_prompt=True,
        )
        ids = self.tokenizer(
            prompt, return_tensors="pt",
        ).input_ids
        out = self.model.generate(
            ids, max_new_tokens=MAX_TOKENS,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        reply = self.tokenizer.decode(
            out[0][ids.shape[1]:],
            skip_special_tokens=True,
        )
        return reply.strip()

    def generate(self, question, passages):
        """Answer from passages, or say so."""
        if not passages:
            return UNKNOWN
        if self.mode == "model":
            try:
                reply = self.model_answer(
                    question, passages,
                )
                if len(reply.split()) < 6:
                    print("Answer too short, "
                          "using template.")
                    return template_answer(
                        question, passages,
                    )
                return reply
            except Exception as e:
                print("Model failed:", e)
                print("Using the template instead.")
                self.mode = "template"
        return template_answer(question, passages)


if __name__ == "__main__":
    import sys
    from retriever import Retriever, load_chunks

    finder = Retriever(load_chunks())
    question = " ".join(sys.argv[1:])
    results = finder.search(question)
    score, chunk = results[0]
    if not finder.trusted(question, score, chunk):
        print(UNKNOWN)
        raise SystemExit
    gen = Generator()
    passages = [c for _, c in results]
    print("Mode:", gen.mode)
    print(gen.generate(question, passages))
