#!/usr/bin/env python3
"""circuit_breaker - Circuit breaker pattern for fault tolerance."""
import sys, time

class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"
    def __init__(self, failure_threshold=3, recovery_timeout=5.0, success_threshold=2):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
    def call(self, func, *args, **kwargs):
        if self.state == self.OPEN:
            if time.monotonic() - self.last_failure_time >= self.recovery_timeout:
                self.state = self.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitOpenError("Circuit is open")
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    def _on_success(self):
        if self.state == self.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = self.CLOSED
                self.failure_count = 0
        elif self.state == self.CLOSED:
            self.failure_count = 0
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN

class CircuitOpenError(Exception):
    pass

def test():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, success_threshold=1)
    # successful calls
    assert cb.call(lambda: 42) == 42
    assert cb.state == cb.CLOSED
    # failures trip the breaker
    for _ in range(2):
        try:
            cb.call(lambda: 1/0)
        except ZeroDivisionError:
            pass
    assert cb.state == cb.OPEN
    # open circuit rejects calls
    try:
        cb.call(lambda: 42)
        assert False
    except CircuitOpenError:
        pass
    # wait for recovery
    time.sleep(0.15)
    assert cb.call(lambda: "ok") == "ok"
    assert cb.state == cb.CLOSED
    print("OK: circuit_breaker")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: circuit_breaker.py test")
