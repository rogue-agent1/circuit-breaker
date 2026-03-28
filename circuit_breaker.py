#!/usr/bin/env python3
"""Circuit breaker pattern."""
import sys,time
class CircuitBreaker:
    def __init__(self,threshold=3,timeout=5):
        self.threshold=threshold;self.timeout=timeout
        self.failures=0;self.state='closed';self.last_fail=0
    def call(self,func,*args):
        if self.state=='open':
            if time.monotonic()-self.last_fail>=self.timeout:
                self.state='half-open'
            else: raise Exception("Circuit OPEN")
        try:
            result=func(*args)
            if self.state=='half-open': self.state='closed';self.failures=0
            return result
        except Exception as e:
            self.failures+=1;self.last_fail=time.monotonic()
            if self.failures>=self.threshold: self.state='open'
            raise
    def __repr__(self): return f"CB(state={self.state}, failures={self.failures})"
def main():
    cb=CircuitBreaker(threshold=3,timeout=1)
    call_count=[0]
    def flaky():
        call_count[0]+=1
        if call_count[0]<=4: raise Exception("Service down")
        return "OK"
    for i in range(8):
        try:
            result=cb.call(flaky)
            print(f"  Call {i+1}: {result} [{cb}]")
        except Exception as e:
            print(f"  Call {i+1}: {e} [{cb}]")
        if cb.state=='open':
            print("  (waiting for timeout...)")
            time.sleep(1.1)
if __name__=="__main__": main()
