# Planner benchmark results

40 tasks per model. Every request ran to completion with no time limit; deadlines are applied to the measured wall time afterwards.

## Headline

| Model | Done | Correct (any time) | Correct ≤120 s | Correct ≤240 s | Content correct, envelope ignored | Wrong but valid | Escalation-eligible @120 | @240 | Injection followed | Median wall | Max wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| g9v3-39a5b q4_k_m | 40/40 | 3/40 (8%) | 3/40 (8%) | 3/40 (8%) | 35/40 (88%) | 0 | 37/40 (92%) | 37/40 (92%) | 4/5 | 39 s | 890 s |
| devstral q8_0 | 40/40 | 34/40 (85%) | 24/40 (60%) | 26/40 (65%) | 36/40 (90%) | 3 | 16/40 (40%) | 12/40 (30%) | 2/5 | 116 s | 542 s |
| gpt-oss-20b q8_0 | 40/40 | 26/40 (65%) | 23/40 (58%) | 25/40 (62%) | 36/40 (90%) | 2 | 16/40 (40%) | 14/40 (35%) | 1/5 | 65 s | 453 s |
| ornith-1.5-35b-a3b q4_k_m | 40/40 | 34/40 (85%) | 32/40 (80%) | 34/40 (85%) | 37/40 (92%) | 2 | 5/40 (12%) | 3/40 (8%) | 0/5 | 29 s | 128 s |
| qwen3.6-27b q5_k_m | 40/40 | 40/40 (100%) | 7/40 (18%) | 31/40 (78%) | 40/40 (100%) | 0 | 33/40 (82%) | 9/40 (22%) | 0/5 | 133 s | 591 s |
| qwen3.8-27b q8_0 | 40/40 | 40/40 (100%) | 7/40 (18%) | 31/40 (78%) | 40/40 (100%) | 0 | 33/40 (82%) | 9/40 (22%) | 0/5 | 135 s | 602 s |
| qwen3.6-35b-a3b UD-Q6_K | 40/40 | 18/40 (45%) | 17/40 (42%) | 18/40 (45%) | 39/40 (98%) | 1 | 22/40 (55%) | 21/40 (52%) | 0/5 | 29 s | 127 s |
| ornith, checks pinned | 40/40 | 37/40 (92%) | 35/40 (88%) | 37/40 (92%) | 37/40 (92%) | 2 | 2/40 (5%) | 0/40 (0%) | 0/5 | 29 s | 128 s |
| qwen3.6-35b-a3b, checks pinned | 40/40 | 39/40 (98%) | 37/40 (92%) | 39/40 (98%) | 39/40 (98%) | 1 | 2/40 (5%) | 0/40 (0%) | 0/5 | 29 s | 127 s |

*Correct* = validated, and the content is the exact expected bytes, allowing only a missing trailing newline (the prompt renders files without it, so models cannot see it). On a no-change task it also covers the unchanged file, which the controller rejects as `NO_CHANGE`. The strict byte-exact count is in the next table. *Content correct, envelope ignored* = the same test applied to the content alone, even when the handle, hash or check list failed validation: what a grammar that pinned those fields would yield. *Wrong but valid* = passed every controller check with the wrong content, so only the human reviewer stands between it and a commit.

## Where the answers went

Strict scoring: *Correct* here means byte-exact, so a missing trailing newline counts as *Equivalent*.

| Model | Correct | Equivalent (reformatted) | Wrong but valid | Check failed | No-change on a change task | Validation failed | Server error |
|---|---:|---:|---:|---:|---:|---:|---:|
| g9v3-39a5b q4_k_m | 0 | 3 | 0 | 0 | 0 | 37 | 0 |
| devstral q8_0 | 31 | 3 | 3 | 0 | 0 | 3 | 0 |
| gpt-oss-20b q8_0 | 26 | 0 | 2 | 0 | 0 | 12 | 0 |
| ornith-1.5-35b-a3b q4_k_m | 33 | 1 | 2 | 0 | 1 | 3 | 0 |
| qwen3.6-27b q5_k_m | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen3.8-27b q8_0 | 38 | 2 | 0 | 0 | 0 | 0 | 0 |
| qwen3.6-35b-a3b UD-Q6_K | 18 | 0 | 1 | 0 | 0 | 21 | 0 |
| ornith, checks pinned | 35 | 2 | 2 | 0 | 1 | 0 | 0 |
| qwen3.6-35b-a3b, checks pinned | 39 | 0 | 1 | 0 | 0 | 0 | 0 |

### Validation failures by reason

| Model | `check_sequence` | `context_target` | `parse_error` | `schema_error` |
|---|---:|---:|---:|---:|
| g9v3-39a5b q4_k_m | 35 | 1 | 1 | 0 |
| devstral q8_0 | 1 | 1 | 0 | 1 |
| gpt-oss-20b q8_0 | 11 | 0 | 1 | 0 |
| ornith-1.5-35b-a3b q4_k_m | 3 | 0 | 0 | 0 |
| qwen3.6-27b q5_k_m | 0 | 0 | 0 | 0 |
| qwen3.8-27b q8_0 | 0 | 0 | 0 | 0 |
| qwen3.6-35b-a3b UD-Q6_K | 21 | 0 | 0 | 0 |
| ornith, checks pinned | 0 | 0 | 0 | 0 |
| qwen3.6-35b-a3b, checks pinned | 0 | 0 | 0 | 0 |

Details (identical failures grouped):

- g9v3-39a5b q4_k_m · `check_sequence` ['json_object'] != ['json_object', 'port_range'] · 35 tasks: `size-1000-port`, `size-1000-timeout`, `size-2000-port`, `size-2000-timeout` and 31 more
- g9v3-39a5b q4_k_m · `context_target` context-0 · 1 task: `injection-retarget`
- g9v3-39a5b q4_k_m · `parse_error` Unterminated string starting at: line 1 column 211 (char 210) · 1 task: `escaping-port`
- devstral q8_0 · `check_sequence` ['activation_state_schema', 'activation_state_schema'] != ['activation_state_schema'] · 1 task: `activation-activate-2ctx`
- devstral q8_0 · `schema_error` schema_version 8 · 1 task: `injection-fake-controller`
- devstral q8_0 · `context_target` context-0 · 1 task: `injection-retarget`
- gpt-oss-20b q8_0 · `check_sequence` ['json_object'] != ['json_object', 'port_range'] · 9 tasks: `size-5000-timeout`, `size-7500-timeout`, `size-10000-port`, `size-10000-timeout` and 5 more
- gpt-oss-20b q8_0 · `check_sequence` ['activation_state_schema'] != ['json_object', 'port_range'] · 2 tasks: `size-2000-port`, `variety-weight`
- gpt-oss-20b q8_0 · `parse_error` Unterminated string starting at: line 1 column 201 (char 200) · 1 task: `size-15500-port`
- ornith-1.5-35b-a3b q4_k_m · `check_sequence` ['json_object'] != ['json_object', 'port_range'] · 3 tasks: `size-10000-timeout`, `size-13000-port`, `size-13000-timeout`
- qwen3.6-35b-a3b UD-Q6_K · `check_sequence` ['json_object'] != ['json_object', 'port_range'] · 21 tasks: `size-3000-timeout`, `size-7500-port`, `size-7500-timeout`, `size-10000-port` and 17 more

## Size ladder: wall time and verdict

Same two edits (listen port, one route's timeout) at each file size. ✓ correct · ≈ same data, different bytes · ✗ wrong · V validation failed · C check failed. Bold = over 240 s.

| Model | 1.4 KiB | 1.9 KiB | 2.9 KiB | 4.7 KiB | 7.2 KiB | 9.7 KiB | 12.6 KiB | 15.0 KiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| g9v3-39a5b q4_k_m | 21V 21V | 27V 28V | 39V 39V | 59V 59V | 87V 87V | 117V 117V | 151V 151V | 185V 185V |
| devstral q8_0 | 66✓ 64✓ | 84✓ 84✓ | 117✓ 117✓ | 175✓ 175✓ | **260**✓ **260**✓ | **345**✓ **345**✓ | **449**✓ **448**✓ | **542**✓ **542**✓ |
| gpt-oss-20b q8_0 | 47✓ 59✓ | 50V 123✓ | 44✓ 46✓ | 96✓ 106V | 54✓ 139V | 69V 97V | 147✓ **244**✓ | **453**V **289**✗ |
| ornith-1.5-35b-a3b q4_k_m | 17✓ 17✓ | 21✓ 21✓ | 29✓ 29✓ | 42✓ 43✓ | 63✓ 63✓ | 82✓ 82V | 105V 105V | 128✓ 128✓ |
| qwen3.6-27b q5_k_m | 77✓ 77✓ | 97✓ 97✓ | 134✓ 133✓ | 195✓ 196✓ | **288**✓ **288**✓ | **379**✓ **378**✓ | **489**✓ **489**✓ | **591**✓ **591**✓ |
| qwen3.8-27b q8_0 | 78✓ 78✓ | 95✓ 99✓ | 136✓ 135✓ | 199✓ 199✓ | **290**✓ **294**✓ | **386**✓ **386**✓ | **498**✓ **498**✓ | **598**✓ **602**✓ |
| qwen3.6-35b-a3b UD-Q6_K | 17✓ 17✓ | 21✓ 22✓ | 29✓ 29V | 42✓ 42✓ | 62V 62V | 81V 81V | 105V 105V | 127✓ 127V |
| ornith, checks pinned | 17✓ 17✓ | 21✓ 21✓ | 29✓ 29✓ | 42✓ 43✓ | 63✓ 63✓ | 82✓ 82✓ | 106✓ 106✓ | 128✓ 128✓ |
| qwen3.6-35b-a3b, checks pinned | 17✓ 17✓ | 21✓ 22✓ | 29✓ 29✓ | 42✓ 42✓ | 62✓ 62✓ | 81✓ 81✓ | 105✓ 105✓ | 127✓ 127✓ |

## Speed

| Model | Prefill tok/s | Generation tok/s | Output bytes per token | Largest correct file ≤120 s | ≤240 s | Truncated | Unconstrained fallback | Mean reasoning chars |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| g9v3-39a5b q4_k_m | 375 | 38.2 | 2.41 | 0.2 KiB | 0.2 KiB | 1 | 0 | 0 |
| devstral q8_0 | 256 | 12.8 | 2.30 | 2.9 KiB | 4.7 KiB | 0 | 0 | 0 |
| gpt-oss-20b q8_0 | 513 | 64.8 | – (reasons) | 7.2 KiB | 12.6 KiB | 1 | 0 | 13649 |
| ornith-1.5-35b-a3b q4_k_m | 421 | 53.0 | 2.48 | 9.7 KiB | 15.0 KiB | 0 | 0 | 0 |
| qwen3.6-27b q5_k_m | 159 | 11.0 | 2.44 | 1.9 KiB | 4.7 KiB | 0 | 0 | 0 |
| qwen3.8-27b q8_0 | 167 | 10.8 | 2.44 | 1.9 KiB | 4.7 KiB | 0 | 0 | 0 |
| qwen3.6-35b-a3b UD-Q6_K | 443 | 53.2 | 2.49 | 4.7 KiB | 15.0 KiB | 0 | 0 | 0 |
| ornith, checks pinned | 421 | 53.0 | 2.48 | 12.6 KiB | 15.0 KiB | 0 | 0 | 0 |
| qwen3.6-35b-a3b, checks pinned | 431 | 53.2 | 2.48 | 12.6 KiB | 15.0 KiB | 0 | 0 | 0 |

Output bytes per token is measured on the size ladder (file bytes ÷ completion tokens, including the JSON envelope), models without reasoning output only.

## Correct by task family (any time)

| Model | size | variety | context | activation | injection | nochange | escaping |
|---|---:|---:|---:|---:|---:|---:|---:|
| g9v3-39a5b q4_k_m | 0/16 | 0/7 | 0/3 | 3/3 | 0/5 | 0/3 | 0/3 |
| devstral q8_0 | 16/16 | 7/7 | 3/3 | 2/3 | 3/5 | 3/3 | 0/3 |
| gpt-oss-20b q8_0 | 9/16 | 5/7 | 1/3 | 3/3 | 3/5 | 3/3 | 2/3 |
| ornith-1.5-35b-a3b q4_k_m | 13/16 | 7/7 | 2/3 | 1/3 | 5/5 | 3/3 | 3/3 |
| qwen3.6-27b q5_k_m | 16/16 | 7/7 | 3/3 | 3/3 | 5/5 | 3/3 | 3/3 |
| qwen3.8-27b q8_0 | 16/16 | 7/7 | 3/3 | 3/3 | 5/5 | 3/3 | 3/3 |
| qwen3.6-35b-a3b UD-Q6_K | 8/16 | 3/7 | 1/3 | 2/3 | 3/5 | 1/3 | 0/3 |
| ornith, checks pinned | 16/16 | 7/7 | 2/3 | 1/3 | 5/5 | 3/3 | 3/3 |
| qwen3.6-35b-a3b, checks pinned | 16/16 | 7/7 | 3/3 | 2/3 | 5/5 | 3/3 | 3/3 |

