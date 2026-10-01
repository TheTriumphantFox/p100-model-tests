#!/usr/bin/env bash
# Event stream for the queue: one line per thing worth knowing. Re-armable -- starts from the
# current end of driver.log, so restarting it does not replay old events.
#   * every leg result, START/DONE, ctx-ladder rung, and any !!! / RIG-FAIL / WARN / ABORT line
#   * STALL: the service is active but nothing under the run dir changed for 30 min
#     (a thinking-on batch can legitimately take ~20 min at 12288 tokens / ~10 tok/s)
#   * the service's terminal state (exited / failed) -- silence is not success
D=/home/hm/Projects/Tests/2026-09-30/qwen36-q8kp
U=${U:-qwen36-q8kp-rerun.service}
touch "$D/driver.log"
tail -n0 -F "$D/driver.log" "$D/watchdog.out" "$D/queue.out" 2>/dev/null \
  | grep --line-buffered -E '!!!|RIG-FAIL|WARN|ABORT|PREFLIGHT|RUN START|RUN DONE| -> |bench_off DONE|think DONE|Traceback|Error|Killed|KILL' &
prev=$(systemctl --user show -p ActiveState --value $U)
stall_flag=0
while true; do
  sleep 60
  st=$(systemctl --user show -p ActiveState --value $U)
  if [ "$st" != "$prev" ]; then
    res=$(systemctl --user show -p Result --value $U); rc=$(systemctl --user show -p ExecMainStatus --value $U)
    echo "SERVICE $prev -> $st (result=$res exit=$rc)"
    prev=$st
  fi
  if [ "$st" = active ]; then
    newest=$(find "$D" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)
    age=$(( $(date +%s) - ${newest%.*} ))
    if [ $age -ge 1800 ] && [ $stall_flag = 0 ]; then
      echo "STALL: service active but nothing written in $((age/60)) min; GPU $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader | tr '\n' ' ')"
      stall_flag=1
    elif [ $age -lt 1800 ]; then stall_flag=0; fi
  fi
done
