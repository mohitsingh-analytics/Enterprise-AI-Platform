import time
import random

def process_job(job_id):
    print(f"Processing {job_id}")
    success = random.choice([True, False])
    if success:
        time.sleep(3)
        print("Loading document...")
        time.sleep(3)    
        print("Creating chunks...")
        time.sleep(3)
        print("Generating embeddings...")
        time.sleep(3)
        print("Saving to vector DB...")
        time.sleep(3)
        print(f"Completed {job_id}")
        return True

    print(f"Job {job_id} failed. Retrying...")

    return False

def process_with_retry(job_id, max_retries=3):
    for attempt in range(1, max_retries+1):
        print(f"Attempt {attempt} for job {job_id}")
        success = process_job(job_id)
        if success:
            return True
        wait_time = 2 ** (attempt-1)
        print(f"Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)

        print(f'{job_id} failed after {max_retries} attempts.Moving it to DLQ.')
        return False

process_with_retry("JOB-101")