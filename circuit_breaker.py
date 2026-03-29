#!/usr/bin/env python3
"""circuit_breaker - Circuit breaker pattern for fault tolerance."""
import argparse, time, random, json

class CircuitBreaker:
    CLOSED = "closed"; OPEN = "open"; HALF_OPEN = "half_open"

    def __init__(self, failure_threshold=5, recovery_timeout=10, success_threshold=3):
        self.state = self.CLOSED
        self.failure_count = 0; self.success_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.last_failure_time = 0
        self.total_calls = 0; self.total_failures = 0

    def call(self, func, *args):
        self.total_calls += 1
        if self.state == self.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = self.HALF_OPEN; self.success_count = 0
            else:
                raise Exception("Circuit is OPEN")
        try:
            result = func(*args)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == self.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = self.CLOSED; self.failure_count = 0
        elif self.state == self.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        self.total_failures += 1; self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN

    def stats(self):
        return {"state": self.state, "failures": self.failure_count,
                "total_calls": self.total_calls, "total_failures": self.total_failures}

def main():
    p = argparse.ArgumentParser(description="Circuit breaker demo")
    p.add_argument("-n", "--calls", type=int, default=30)
    p.add_argument("--fail-rate", type=float, default=0.4)
    p.add_argument("--threshold", type=int, default=3)
    p.add_argument("--timeout", type=float, default=2)
    args = p.parse_args()
    cb = CircuitBreaker(args.threshold, args.timeout)
    def unreliable_service():
        if random.random() < args.fail_rate: raise Exception("Service failed")
        return "OK"
    successes = failures = blocked = 0
    for i in range(args.calls):
        try:
            cb.call(unreliable_service); successes += 1
            print(f"  Call {i}: OK [{cb.state}]")
        except Exception as e:
            if "OPEN" in str(e): blocked += 1; print(f"  Call {i}: BLOCKED [{cb.state}]")
            else: failures += 1; print(f"  Call {i}: FAIL [{cb.state}]")
        time.sleep(0.3)
    print(f"\nResults: {successes} ok, {failures} failed, {blocked} blocked")
    print(json.dumps(cb.stats(), indent=2))

if __name__ == "__main__":
    main()
