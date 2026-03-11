#!/usr/bin/env python3
"""circuit_breaker — Circuit breaker pattern for fault tolerance. Zero deps."""
import time

CLOSED, OPEN, HALF_OPEN = 'closed', 'open', 'half_open'

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=5.0, success_threshold=2):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.state = CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = 0
        self.total_calls = 0
        self.total_failures = 0

    def call(self, fn, *args, **kwargs):
        self.total_calls += 1
        if self.state == OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = HALF_OPEN
                self.successes = 0
            else:
                raise CircuitOpenError(f"Circuit is OPEN (failures={self.failures})")
        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CLOSED
                self.failures = 0
        else:
            self.failures = 0

    def _on_failure(self):
        self.failures += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = OPEN

    @property
    def stats(self):
        return {
            'state': self.state, 'failures': self.failures,
            'total_calls': self.total_calls, 'total_failures': self.total_failures,
            'error_rate': self.total_failures / self.total_calls if self.total_calls else 0
        }

class CircuitOpenError(Exception):
    pass

def main():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.5)
    call_count = [0]

    def flaky_service():
        call_count[0] += 1
        if call_count[0] <= 4:
            raise ConnectionError(f"Service down (call {call_count[0]})")
        return f"OK (call {call_count[0]})"

    print("Circuit Breaker Demo:\n")
    for i in range(8):
        try:
            result = cb.call(flaky_service)
            print(f"  Call {i+1}: {result} [{cb.state}]")
        except CircuitOpenError as e:
            print(f"  Call {i+1}: BLOCKED - {e}")
        except ConnectionError as e:
            print(f"  Call {i+1}: FAILED - {e} [{cb.state}]")
        if i == 4:
            print("  (waiting for recovery timeout...)")
            time.sleep(0.6)
            call_count[0] = 5  # service recovers

    print(f"\nStats: {cb.stats}")

if __name__ == "__main__":
    main()
