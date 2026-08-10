import time

class CircuitBreaker:
    def __init__(self, failure_threshold, recovery_time):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_time
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def call(self, function):
        # If circuit is open, check timeout
        if self.state == "OPEN":
            if self.last_failure_time is None:
                # safety: treat as open
                print("Circuit is OPEN. Rejecting the request.")
                return False
            elapsed = time.time() - self.last_failure_time
            print("elapsed time ********", elapsed)
            if elapsed < self.recovery_timeout:
                print("Circuit is OPEN. Rejecting the request.")
                return False
            else:
                print("Circuit is in HALF-OPEN state. Trying the request again.")
                self.state = "HALF-OPEN"

        try:
            result = function()
            print("Function executed successfully.")
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            # record failure
            self.failure_count += 1
            self.last_failure_time = time.time()
            print(f"Function failed, failures: {self.failure_count}. Error: {e}")
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                print("Failure threshold reached. Circuit opened.")
            
            return False


def embedding_service():

    print("Calling embedding service...")

    raise Exception("Embedding service unavailable")


breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_time=5
)



for i in range(6):

    print(f"\nRequest {i + 1}")

    breaker.call(embedding_service)

    time.sleep(3)