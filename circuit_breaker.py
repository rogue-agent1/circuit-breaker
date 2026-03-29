#!/usr/bin/env python3
"""Circuit breaker for fault-tolerant service calls."""
import sys, time

class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"
    def __init__(self, failure_threshold=5, recovery_timeout=30, success_threshold=2):
        self.state = self.CLOSED
        self.failures = 0; self.successes = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.last_failure_time = 0
    def call(self, fn, *args, **kwargs):
        if self.state == self.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = self.HALF_OPEN; self.successes = 0
            else: raise Exception("Circuit is OPEN")
        try:
            result = fn(*args, **kwargs)
            self._on_success(); return result
        except Exception as e:
            self._on_failure(); raise
    def _on_success(self):
        if self.state == self.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = self.CLOSED; self.failures = 0
        else: self.failures = 0
    def _on_failure(self):
        self.failures += 1; self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = self.OPEN

def main():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    call_count = [0]
    def flaky_service():
        call_count[0] += 1
        if call_count[0] <= 4: raise Exception("Service down")
        return "OK"
    for i in range(8):
        try:
            result = cb.call(flaky_service)
            print(f"  Call {i}: {result} (state={cb.state})")
        except Exception as e:
            print(f"  Call {i}: {e} (state={cb.state})")
        if cb.state == "open": time.sleep(1.1)

if __name__ == "__main__": main()
