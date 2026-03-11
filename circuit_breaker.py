#!/usr/bin/env python3
"""Circuit breaker pattern."""
import sys, time, random
random.seed(42)
class CircuitBreaker:
    def __init__(self,threshold=3,timeout=5):
        self.threshold=threshold; self.timeout=timeout
        self.failures=0; self.state='CLOSED'; self.last_fail=0
    def call(self,fn,*args):
        if self.state=='OPEN':
            if time.time()-self.last_fail>self.timeout:
                self.state='HALF_OPEN'; print(f"    [CB] → HALF_OPEN")
            else: raise Exception("Circuit OPEN")
        try:
            result=fn(*args)
            if self.state=='HALF_OPEN': self.state='CLOSED'; self.failures=0; print(f"    [CB] → CLOSED")
            return result
        except Exception as e:
            self.failures+=1; self.last_fail=time.time()
            if self.failures>=self.threshold:
                self.state='OPEN'; print(f"    [CB] → OPEN (failures={self.failures})")
            raise
def flaky_service():
    if random.random()<0.5: raise Exception("Service error")
    return "OK"
cb=CircuitBreaker(threshold=3,timeout=2)
print("Circuit Breaker Demo:")
for i in range(10):
    try:
        result=cb.call(flaky_service)
        print(f"  Call {i}: {result} (state={cb.state})")
    except Exception as e:
        print(f"  Call {i}: FAIL - {e} (state={cb.state})")
    time.sleep(0.5)
