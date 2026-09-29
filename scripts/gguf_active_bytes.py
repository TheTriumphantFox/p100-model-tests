#!/usr/bin/env python3
"""Per-token ACTIVE bytes for a GGUF - what a bandwidth-bound box actually reads.

    gguf-active-bytes.py <blob>=<label> [<blob>=<label> ...]

Resolve a tag to its blob with: ollama show --modelfile <tag> | awk '/^FROM .*blobs/{print $2}'

Generation reads every weight once per token, so tok/s ~ effective_bandwidth / active_bytes.
For MoE only the routed experts are read, which is why an A3B model is many times faster
here than a dense model of the same file size. token_embd is excluded: it is a one-row
gather, not a stream.
"""
import struct, sys, collections

# ggml type -> (elements per block, bytes per block)
TS = {0:(1,4), 1:(1,2), 2:(32,18), 3:(32,20), 6:(32,24), 7:(32,24), 8:(32,34), 9:(32,36),
      10:(256,84), 11:(256,110), 12:(256,110), 13:(256,144), 14:(256,210), 15:(256,292),
      16:(256,66), 17:(256,74), 18:(256,98), 19:(256,50), 20:(256,110), 21:(256,78),
      22:(256,86), 23:(256,102), 24:(1,1), 25:(1,2), 26:(1,4), 27:(1,8), 28:(1,8),
      29:(256,512), 30:(1,2)}
TNAME = {0:'F32',1:'F16',2:'Q4_0',3:'Q4_1',6:'Q5_0',7:'Q5_1',8:'Q8_0',9:'Q8_1',10:'Q2_K',
         11:'Q3_K',12:'Q4_K',13:'Q5_K',14:'Q6_K',15:'Q8_K',16:'IQ2_XXS',17:'IQ2_XS',
         18:'IQ3_XXS',19:'IQ1_S',20:'IQ4_NL',21:'IQ3_S',22:'IQ2_S',23:'IQ4_XS',30:'BF16'}
SCALAR = {0:'<B',1:'<b',2:'<H',3:'<h',4:'<I',5:'<i',6:'<f',7:'<?',10:'<Q',11:'<q',12:'<d'}

def parse(path):
    f = open(path, 'rb')
    def r(fmt): return struct.unpack(fmt, f.read(struct.calcsize(fmt)))[0]
    assert f.read(4) == b'GGUF', 'not a GGUF file'
    r('<I'); n_tensors = r('<Q'); n_kv = r('<Q')
    def rstr():
        n = r('<Q'); return f.read(n).decode('utf-8', 'replace')
    def rval(t):
        if t == 8: return rstr()
        if t == 9:
            et = r('<I'); n = r('<Q')
            for _ in range(n):
                rstr() if et == 8 else rval(et)
            return f'<list n={n}>'
        return r(SCALAR[t])
    kv = {}
    for _ in range(n_kv):
        k = rstr(); kv[k] = rval(r('<I'))
    rows = []
    for _ in range(n_tensors):
        name = rstr(); nd = r('<I'); dims = [r('<Q') for _ in range(nd)]; tt = r('<I'); r('<Q')
        ne = 1
        for d in dims: ne *= d
        be, bb = TS[tt]
        rows.append((name, ne * bb // be, tt, ne))
    return kv, rows

def num(x): return x if isinstance(x, (int, float)) else None

for arg in sys.argv[1:]:
    path, label = arg.split('=', 1)
    kv, rows = parse(path)
    arch = kv.get('general.architecture')
    def g(key, d=None): return kv.get(f'{arch}.{key}', d)
    nexp, nused = g('expert_count', 0) or 0, g('expert_used_count', 0) or 0
    nl, kvh = num(g('block_count')), num(g('attention.head_count_kv'))
    kl, vl = num(g('attention.key_length')) or 128, num(g('attention.value_length')) or 128
    total = sum(b for _, b, _, _ in rows)
    emb = sum(b for n, b, _, _ in rows if 'token_embd' in n)
    exps = sum(b for n, b, _, _ in rows if '_exps' in n)
    active = (total - emb - exps) + (exps * nused / nexp if nexp else 0)
    params = sum(ne for _, _, _, ne in rows)
    dom = collections.Counter({TNAME.get(t, t): 0 for _, _, t, _ in rows})
    for _, b, t, _ in rows: dom[TNAME.get(t, t)] += b
    kv_f16 = 2 * nl * kvh * (kl + vl) / 2 * 2 if (nl and kvh) else 0
    print(f"{label}")
    print(f"  arch {arch}  layers {nl}  dominant {dom.most_common(1)[0][0]}  bpw {total*8/params:.2f}")
    moe = f"  experts {exps/1e9:.2f} GB ({nused}/{nexp} routed)" if nexp else "  dense"
    print(f"  file {total/1e9:6.2f} GB   embed {emb/1e9:4.2f} GB{moe}")
    print(f"  ACTIVE {active/1e9:6.2f} GB/token    KV {kv_f16/1024:5.1f} KiB/token f16, "
          f"{kv_f16*34/32/2/1024:5.1f} KiB q8_0")
    print()
