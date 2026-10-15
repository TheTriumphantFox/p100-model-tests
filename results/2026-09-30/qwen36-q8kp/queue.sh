#!/usr/bin/env bash
# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
# Run every candidate in turn against the incumbent. Detach it:
#   nohup ./queue.sh > queue.out 2>&1 &
# Order: the Unsloth Q8_0 first -- a plain Q8_0 is known to fit and run here (the Qwen3.8
# Q8_0 did), so its numbers land even if the tight 31.96 GB Q8_K_P will not load.
HERE=$(cd "$(dirname "$0")" && pwd)
"$HERE/run.sh" qwen3.6-27b-unsloth_q8_0      qwen3.6-27b-unsloth:q8_0       unsloth-q8
"$HERE/run.sh" qwen3.6-27b-abliterated_q8_k_p qwen3.6-27b-abliterated:q8_k_p q8kp
