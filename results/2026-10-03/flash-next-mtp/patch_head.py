#!/usr/bin/env python3
"""Make ggml-org's detached Flash-Next MTP head loadable by PR ggml-org/llama.cpp#27836.

The PR loads a detached head as a full qwen4exp model, so it requires the trunk's top-level
head mixer (output_hc_norm / output_hc_down / output_hc_up) even though graph_mtp collapses
the residual with the head's own blk.N.nextn.hc_head_*. ggml-org's head file omits them.
This copies every KV and tensor of the head unchanged and appends those three tensors,
byte-for-byte, from the trunk GGUF they belong to (13 MB, same model, same weights).

    patch_head.py <head.gguf> <trunk-00001.gguf> <out.gguf>
"""
import sys

import gguf

head_p, trunk_p, out_p = sys.argv[1:4]
head = gguf.GGUFReader(head_p)
trunk = gguf.GGUFReader(trunk_p)
WANT = ["output_hc_norm.weight", "output_hc_down.weight", "output_hc_up.weight"]
have = {t.name for t in head.tensors}
extra = [t for t in trunk.tensors if t.name in WANT and t.name not in have]
assert len(extra) == len([w for w in WANT if w not in have]), f"trunk lacks some of {WANT}"

arch = head.fields[gguf.Keys.General.ARCHITECTURE].contents()
w = gguf.GGUFWriter(out_p, arch=arch, endianess=head.endianess)
for f in head.fields.values():
    if f.name == gguf.Keys.General.ARCHITECTURE or f.name.startswith("GGUF."):
        continue
    vt = f.types[0]
    st = f.types[-1] if vt == gguf.GGUFValueType.ARRAY else None
    w.add_key_value(f.name, f.contents(), vt, sub_type=st)

tensors = list(head.tensors) + extra
for t in tensors:
    w.add_tensor_info(t.name, t.data.shape, t.data.dtype, t.data.nbytes, t.tensor_type)
w.write_header_to_file()
w.write_kv_data_to_file()
w.write_ti_data_to_file()
for t in tensors:
    w.write_tensor_data(t.data, tensor_endianess=head.endianess)
w.close()
print(f"wrote {out_p}: {len(head.tensors)} head tensors + {[t.name for t in extra]}")
