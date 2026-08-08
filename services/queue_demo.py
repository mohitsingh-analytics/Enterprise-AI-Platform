from queue import Queue
import threading
import time

job_queue = Queue()


def worker():
    
    job = job_queue.get()

    print(f"Processing {job['job_id']}")
    time.sleep(3)
    print("Loading document...")
    time.sleep(3)    
    print("Creating chunks...")
    time.sleep(3)
    print("Generating embeddings...")
    time.sleep(3)
    print("Saving to vector DB...")
    time.sleep(3)
    print(f"Completed {job['job_id']}")
    time.sleep(3)
    job_queue.task_done()


def submit_document(file_name):

    job = {
        "job_id": "JOB-001 {file_name}",
        "document": file_name
    }

    job_queue.put(job)

    return {
        "success": True,
        "message": "Document accepted for processing.",
        "job_id": job["job_id"]
    }

thread = threading.Thread(target=worker)
thread.start()

input_file=[]
for i in range(3):
    time.sleep(1)
    print(i)
    doc_name = input("Enter document name to submit: ")
    input_file.append(doc_name)
    response = submit_document(input_file[i])
    print(response)

thread.join()