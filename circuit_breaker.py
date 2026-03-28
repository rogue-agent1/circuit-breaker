#!/usr/bin/env python3
"""Circuit breaker pattern — zero-dep."""
import time

class CircuitBreaker:
    CLOSED="CLOSED"; OPEN="OPEN"; HALF_OPEN="HALF_OPEN"
    def __init__(self, failure_threshold=3, recovery_timeout=5, success_threshold=2):
        self.state=self.CLOSED; self.failures=0; self.successes=0
        self.failure_threshold=failure_threshold
        self.recovery_timeout=recovery_timeout
        self.success_threshold=success_threshold
        self.last_failure_time=0; self.log=[]
    def call(self, fn, *args, **kwargs):
        if self.state==self.OPEN:
            if time.monotonic()-self.last_failure_time>self.recovery_timeout:
                self.state=self.HALF_OPEN; self.log.append("→ HALF_OPEN")
            else:
                self.log.append(f"BLOCKED (OPEN)"); raise RuntimeError("Circuit is OPEN")
        try:
            result=fn(*args,**kwargs)
            self._on_success(); return result
        except Exception as e:
            self._on_failure(); raise
    def _on_success(self):
        if self.state==self.HALF_OPEN:
            self.successes+=1
            if self.successes>=self.success_threshold:
                self.state=self.CLOSED; self.failures=0; self.successes=0
                self.log.append("→ CLOSED (recovered)")
        self.failures=0
    def _on_failure(self):
        self.failures+=1; self.last_failure_time=time.monotonic()
        if self.failures>=self.failure_threshold:
            self.state=self.OPEN; self.log.append(f"→ OPEN (failures={self.failures})")

if __name__=="__main__":
    cb=CircuitBreaker(failure_threshold=3,recovery_timeout=0.5)
    call_count=[0]
    def unreliable():
        call_count[0]+=1
        if call_count[0]<=4: raise ConnectionError("Service down")
        return "OK"
    for i in range(8):
        try:
            r=cb.call(unreliable)
            print(f"  Call {i+1}: {r} [{cb.state}]")
        except Exception as e:
            print(f"  Call {i+1}: {type(e).__name__} [{cb.state}]")
        if cb.state==cb.OPEN: time.sleep(0.6)
    print("Log:"); [print(f"  {l}") for l in cb.log]
