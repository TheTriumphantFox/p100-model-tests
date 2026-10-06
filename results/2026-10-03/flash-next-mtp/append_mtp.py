#!/usr/bin/env python3
"""Append a Flash-Next MTP head to a qwen4exp trunk as trailing block N, the layout PR
ggml-org/llama.cpp#27836 loads (`--spec-type draft-mtp`, no -md). The PR does not load a
detached head: as a draft model it is parsed as a whole qwen4exp model and wants every trunk
tensor.

Only shard 1 of the trunk is rewritten: every KV and tensor copied byte-for-byte, plus
  block_count               48 -> 49
  nextn_predict_layers      = 1
  attention.compress_ratios + [0]       (PR converter: trailing MTP block attends densely)
  attention.recurrent_layers  = head's 49-entry array, only if the trunk carries one
  split.tensors.count       += number of head tensors added
and the head's blk.<N>.* tensors appended (its token_embd/output copies are dropped; the
trunk's own are used, as the PR's graph_mtp reuses the trunk LM head). Later shards are
unchanged and can be hard-linked next to the output under the new prefix.

    append_mtp.py <trunk-00001-of-000NN.gguf> <head.gguf> <out-00001-of-000NN.gguf>
"""
import sys

import gguf

trunk_p, head_p, out_p = sys.argv[1:4]
tr = gguf.GGUFReader(trunk_p)
hd = gguf.GGUFReader(head_p)
arch = tr.fields[gguf.Keys.General.ARCHITECTURE].contents()
n = tr.fields[f"{arch}.block_count"].contents()
add = [t for t in hd.tensors if t.name.startswith(f"blk.{n}.")]
assert add, f"head has no blk.{n}.* tensors"
assert not any(t.name.startswith(f"blk.{n}.") for t in tr.tensors), "trunk already has an MTP block"

new = {
    f"{arch}.block_count": (n + 1, gguf.GGUFValueType.UINT32, None),
    f"{arch}.nextn_predict_layers": (1, gguf.GGUFValueType.UINT32, None),
}
cr = tr.fields[f"{arch}.attention.compress_ratios"]
new[cr.name] = (list(cr.contents()) + [0], gguf.GGUFValueType.ARRAY, cr.types[-1])
rl = f"{arch}.attention.recurrent_layers"
if rl in tr.fields:
    new[rl] = (hd.fields[rl].contents(), gguf.GGUFValueType.ARRAY, hd.fields[rl].types[-1])
if "split.tensors.count" in tr.fields:
    c = tr.fields["split.tensors.count"]
    new["split.tensors.count"] = (c.contents() + len(add), c.types[0], None)

w = gguf.GGUFWriter(out_p, arch=arch, endianess=tr.endianess)
seen = set()
for f in tr.fields.values():
    if f.name == gguf.Keys.General.ARCHITECTURE or f.name.startswith("GGUF."):
        continue
    seen.add(f.name)
    if f.name in new:
        v, vt, st = new[f.name]
        w.add_key_value(f.name, v, vt, sub_type=st)
        continue
    vt = f.types[0]
    st = f.types[-1] if vt == gguf.GGUFValueType.ARRAY else None
    w.add_key_value(f.name, f.contents(), vt, sub_type=st)
for k, (v, vt, st) in new.items():
    if k not in seen:
        w.add_key_value(k, v, vt, sub_type=st)

tensors = list(tr.tensors) + add
for t in tensors:
    w.add_tensor_info(t.name, t.data.shape, t.data.dtype, t.data.nbytes, t.tensor_type)
w.write_header_to_file()
w.write_kv_data_to_file()
w.write_ti_data_to_file()
done = 0
for i, t in enumerate(tensors):
    w.write_tensor_data(t.data, tensor_endianess=tr.endianess)
    done += int(t.n_bytes)
    if i % 100 == 0:
        print(f"{done/1e9:.1f} GB", flush=True)
w.close()
print(f"wrote {out_p}: {len(tr.tensors)} trunk + {len(add)} head tensors; block_count {n}->{n+1}")
