"""Split the notes into short passages.

Reads every docs/*.txt file, splits it into
paragraph blocks, and packs them into chunks
of at most 500 characters. A chunk keeps the
lecture it came from and its section heading.

Run: python chunk_notes.py
Writes: chunks.json
"""

import glob
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
OUT = os.path.join(BASE, "chunks.json")
MAX_LEN = 500


def is_heading(block):
    """A short line with no full stop."""
    if len(block) > 60:
        return False
    if "." in block:
        return False
    return True


def split_long(text):
    """Split one long line into word-sized parts."""
    words = text.split(" ")
    parts = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > MAX_LEN:
            parts.append(current)
            current = word
        else:
            join = " " if current else ""
            current = current + join + word
    if current:
        parts.append(current)
    return parts


def split_sentences(text):
    """Split on sentence ends, keep the stops."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def pack(blocks, source, section, chunks):
    """Pack blocks into chunks under MAX_LEN."""
    current = ""

    def flush():
        nonlocal current
        if current:
            chunks.append(make(source, section, current))
            current = ""

    def add(text):
        nonlocal current
        if len(current) + len(text) + 1 > MAX_LEN:
            flush()
        join = " " if current else ""
        current = current + join + text

    for block in blocks:
        if len(block) > MAX_LEN:
            flush()
            for sent in split_sentences(block):
                for piece in split_long(sent):
                    add(piece)
        else:
            add(block)
    flush()


def make(source, section, text):
    return {"source": source,
            "section": section,
            "text": text}


def chunk_file(path):
    """Chunk one notes file, return its chunks."""
    with open(path) as f:
        raw = f.read()
    lines = raw.split("\n")
    source = lines[0].strip()
    blocks = []
    buf = []
    for line in lines[2:]:
        line = line.strip()
        if line == "":
            if buf:
                blocks.append(" ".join(buf))
                buf = []
        else:
            buf.append(line)
    if buf:
        blocks.append(" ".join(buf))
    chunks = []
    section = ""
    group = []
    for block in blocks:
        if is_heading(block):
            if group:
                pack(group, source, section, chunks)
                group = []
            section = block
        else:
            group.append(block)
    if group:
        pack(group, source, section, chunks)
    return chunks


def main():
    all_chunks = []
    for path in sorted(glob.glob(DOCS + "/*.txt")):
        got = chunk_file(path)
        print(os.path.basename(path), "->", len(got),
              "chunks")
        all_chunks.extend(got)
    for i, chunk in enumerate(all_chunks):
        chunk["id"] = i
    with open(OUT, "w") as f:
        json.dump(all_chunks, f, indent=2)
    print("Total chunks:", len(all_chunks))


if __name__ == "__main__":
    main()
