#!/usr/bin/env python3
"""circuit_breaker - Circuit breaker pattern for fault tolerance."""
import sys,time,random
class CircuitBreaker:
    def __init__(s,threshold=5,timeout=10,half_open_max=1):
        s.threshold=threshold;s.timeout=timeout;s.half_open_max=half_open_max
        s.failures=0;s.state="closed";s.last_failure=0;s.half_open_calls=0
    def call(s,fn,*args):
        if s.state=="open":
            if time.time()-s.last_failure>s.timeout:s.state="half_open";s.half_open_calls=0
            else:raise Exception("Circuit is OPEN")
        if s.state=="half_open" and s.half_open_calls>=s.half_open_max:raise Exception("Circuit is HALF-OPEN (limit)")
        try:
            result=fn(*args)
            if s.state=="half_open":s.state="closed";s.failures=0
            else:s.failures=0
            return result
        except Exception as e:
            s.failures+=1;s.last_failure=time.time()
            if s.state=="half_open":s.state="open"
            elif s.failures>=s.threshold:s.state="open"
            raise
    def __repr__(s):return f"CB(state={s.state}, failures={s.failures})"
if __name__=="__main__":
    cb=CircuitBreaker(threshold=3,timeout=2)
    def flaky_service(fail=False):
        if fail:raise Exception("Service down!")
        return "OK"
    for i in range(10):
        try:result=cb.call(flaky_service,i<4);print(f"  Call {i}: {result} {cb}")
        except Exception as e:print(f"  Call {i}: {e} {cb}")
    print("\nWaiting for timeout...");time.sleep(2.1)
    try:print(f"  Recovery: {cb.call(flaky_service,False)} {cb}")
    except:print(f"  Still broken {cb}")
