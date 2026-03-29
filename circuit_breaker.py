#!/usr/bin/env python3
"""Circuit breaker pattern implementation for fault tolerance."""
import sys, time, threading, random

class CircuitBreaker:
    CLOSED = "closed"; OPEN = "open"; HALF_OPEN = "half-open"
    def __init__(self, failure_threshold=5, recovery_timeout=30, success_threshold=3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.state = self.CLOSED; self.failures = 0; self.successes = 0
        self.last_failure = None; self.lock = threading.Lock()
        self.stats = {"total": 0, "success": 0, "failure": 0, "rejected": 0}

    def call(self, fn, *args, **kwargs):
        with self.lock:
            self.stats["total"] += 1
            if self.state == self.OPEN:
                if time.time() - self.last_failure >= self.recovery_timeout:
                    self.state = self.HALF_OPEN; self.successes = 0
                else:
                    self.stats["rejected"] += 1
                    raise Exception("Circuit is OPEN")
        try:
            result = fn(*args, **kwargs)
            with self.lock:
                self.stats["success"] += 1
                if self.state == self.HALF_OPEN:
                    self.successes += 1
                    if self.successes >= self.success_threshold:
                        self.state = self.CLOSED; self.failures = 0
                elif self.state == self.CLOSED: self.failures = 0
            return result
        except Exception as e:
            with self.lock:
                self.stats["failure"] += 1; self.failures += 1; self.last_failure = time.time()
                if self.failures >= self.failure_threshold:
                    self.state = self.OPEN
            raise

    def status(self):
        return f"State: {self.state} | Failures: {self.failures}/{self.failure_threshold} | Stats: {self.stats}"

def demo():
    print("=== Circuit Breaker Demo ===\n")
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=2, success_threshold=2)
    fail_rate = [0.0]

    def unreliable_service():
        if random.random() < fail_rate[0]: raise Exception("Service error")
        return "OK"

    # Normal operation
    print("Phase 1: Normal operation")
    for i in range(5):
        try: r = cb.call(unreliable_service); print(f"  Call {i+1}: {r}")
        except Exception as e: print(f"  Call {i+1}: {e}")
    print(f"  {cb.status()}\n")

    # Failures trigger open
    print("Phase 2: Service degradation (80% failure)")
    fail_rate[0] = 0.8
    for i in range(10):
        try: r = cb.call(unreliable_service); print(f"  Call {i+1}: {r}")
        except Exception as e: print(f"  Call {i+1}: {e}")
    print(f"  {cb.status()}\n")

    # Recovery
    print("Phase 3: Waiting for recovery timeout...")
    time.sleep(2.5)
    fail_rate[0] = 0.0
    for i in range(5):
        try: r = cb.call(unreliable_service); print(f"  Call {i+1}: {r}")
        except Exception as e: print(f"  Call {i+1}: {e}")
    print(f"  {cb.status()}")

def main(): demo()
if __name__ == "__main__": main()
