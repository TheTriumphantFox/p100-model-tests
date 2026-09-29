#!/usr/bin/env python3
"""Read the metadata header of a GGUF file, or of an Ollama tag's weight blob.

Ollama tag names say nothing reliable about what a model actually is: two names can
share one blob, and a name like `qwen3.6-35b-a3b` can be a third-party abliteration
rather than the stock release. The GGUF header is the primary source. The keys worth
reading are `general.name`, `general.basename`, `general.finetune`,
`general.license.link` and `general.dataset.*` (a `KL<number>` basename is the
signature of an abliterated model).

Only the standard library is used, and only the header is read, so this is fast even
on a 40 GB file.

Usage:
    gguf_meta.py <path-to.gguf>          # read a file directly
    gguf_meta.py --tag <ollama-tag>      # resolve the tag's blob, then read it
    gguf_meta.py --tag <tag> --all       # include tokenizer.ggml.* keys
    gguf_meta.py --survey                # provenance line for every installed tag
"""

from __future__ import annotations

import argparse
import json
import struct
import subprocess
import sys

# GGUF metadata value type tags, in spec order.
(T_U8, T_I8, T_U16, T_I16, T_U32, T_I32,
 T_F32, T_BOOL, T_STR, T_ARR, T_U64, T_I64, T_F64) = range(13)

WIDTH = {T_U8: 1, T_I8: 1, T_U16: 2, T_I16: 2, T_U32: 4,
         T_I32: 4, T_F32: 4, T_BOOL: 1, T_U64: 8, T_I64: 8, T_F64: 8}
FORMAT = {T_U8: "<B", T_I8: "<b", T_U16: "<H", T_I16: "<h", T_U32: "<I",
          T_I32: "<i", T_F32: "<f", T_BOOL: "<?", T_U64: "<Q", T_I64: "<q", T_F64: "<d"}

# Token lists run to hundreds of thousands of entries; skip past them rather than hold them.
INLINE_ARRAY_LIMIT = 64

# The provenance keys, in the order worth reading them.
PROVENANCE = ("general.name", "general.basename", "general.finetune", "general.size_label",
              "general.version", "general.license", "general.license.link",
              "general.architecture", "general.parameter_count", "general.file_type")


class Reader:
    def __init__(self, fh):
        self.fh = fh

    def u32(self) -> int:
        return struct.unpack("<I", self.fh.read(4))[0]

    def u64(self) -> int:
        return struct.unpack("<Q", self.fh.read(8))[0]

    def string(self) -> str:
        return self.fh.read(self.u64()).decode("utf-8", "replace")

    def value(self, vtype: int):
        if vtype == T_STR:
            return self.string()
        if vtype == T_ARR:
            etype, count = self.u32(), self.u64()
            if etype == T_STR:
                if count > INLINE_ARRAY_LIMIT:
                    for _ in range(count):
                        self.string()
                    return f"<{count} strings omitted>"
                return [self.string() for _ in range(count)]
            if etype == T_ARR:
                return "<nested array>"
            raw = self.fh.read(WIDTH[etype] * count)
            if count > INLINE_ARRAY_LIMIT:
                return f"<{count} numbers omitted>"
            return list(struct.unpack(f"<{count}{FORMAT[etype][1]}", raw))
        return struct.unpack(FORMAT[vtype], self.fh.read(WIDTH[vtype]))[0]


def read_header(path: str) -> tuple[int, int, dict]:
    """Return (gguf_version, tensor_count, metadata) for the file at path."""
    with open(path, "rb") as fh:
        reader = Reader(fh)
        if fh.read(4) != b"GGUF":
            raise ValueError(f"not a GGUF file: {path}")
        version, tensors, pairs = reader.u32(), reader.u64(), reader.u64()
        meta: dict = {}
        for _ in range(pairs):
            key = reader.string()
            vtype = reader.u32()
            try:
                meta[key] = reader.value(vtype)
            except Exception as exc:                     # truncated or unknown type
                meta[key] = f"<unreadable: {exc}>"
                break
        return version, tensors, meta


def blob_for_tag(tag: str) -> str:
    """Resolve an Ollama tag to the path of its weight blob."""
    out = subprocess.run(["ollama", "show", "--modelfile", tag],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("FROM /"):
            return line.split(None, 1)[1].strip()
    raise SystemExit(f"could not resolve a blob for tag: {tag}")


def installed_tags() -> list[str]:
    out = subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout
    return [line.split()[0] for line in out.splitlines()[1:] if line.strip()]


def survey() -> None:
    """One provenance line per installed tag, so shared blobs are obvious."""
    for tag in installed_tags():
        blob = blob_for_tag(tag)
        _, _, meta = read_header(blob)
        digest = blob.rsplit("sha256-", 1)[-1][:12]
        name = meta.get("general.name", "?")
        basename = meta.get("general.basename", "")
        finetune = meta.get("general.finetune", "")
        # Two different signatures: a KL-budget basename, or the name saying so outright.
        haystack = f"{name} {basename} {finetune}".lower()
        abliterated = (str(basename).startswith("KL")
                       or "uncensored" in haystack or "hauhaucs" in haystack)
        marker = "  <- abliterated" if abliterated else ""
        print(f"{digest}  {tag}")
        print(f"              {name}  [basename {basename}, finetune {finetune}]{marker}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", help="path to a .gguf file")
    ap.add_argument("--tag", help="an Ollama tag; its weight blob is read instead")
    ap.add_argument("--all", action="store_true", help="include tokenizer.ggml.* keys")
    ap.add_argument("--survey", action="store_true",
                    help="print a provenance line for every installed Ollama tag")
    args = ap.parse_args()

    if args.survey:
        survey()
        return

    path = blob_for_tag(args.tag) if args.tag else args.path
    if not path:
        ap.error("give a path, or --tag, or --survey")

    version, tensors, meta = read_header(path)
    if not args.all:
        meta = {k: v for k, v in meta.items() if not k.startswith("tokenizer.ggml.")}

    print(f"# {path}")
    print(f"# gguf v{version}, {tensors} tensors, {len(meta)} metadata keys\n")
    for key in PROVENANCE:
        if key in meta:
            print(f"{key:32} {meta[key]}")
    print()
    rest = {k: v for k, v in meta.items() if k not in PROVENANCE}
    print(json.dumps(rest, indent=1))


if __name__ == "__main__":
    main()
