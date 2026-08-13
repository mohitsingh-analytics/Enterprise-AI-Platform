import time
import threading

# ---------------------------------------
# WRITE MODEL
# ---------------------------------------

write_store = {}

# ---------------------------------------
# EVENT BUS
# ---------------------------------------

event_queue = []

# ---------------------------------------
# READ MODEL
# ---------------------------------------

read_model = {}

def upload_document(document_id, file_name):

    print("\n[WRITE] Receiving document...")

    write_store[document_id] = {
        "document_id": document_id,
        "file_name": file_name,
        "status": "PROCESSING"
    }

    event = {
        "event_type": "DocumentUploaded",
        "document_id": document_id,
        "file_name": file_name,
        "status": "PROCESSING",
        "embedding_version": "v1"
    }

    event_queue.append(event)

    print("[WRITE] Document stored successfully.")
    print("[WRITE] Event published.")

    return write_store[document_id]

def update_document_status(document_id, status):
    print("\n[READ] Updating document status...")

    if document_id not in read_model:
        print("[READ] Document not found.")
        return None

    read_model[document_id]["status"] = status

    event = {
        "event_type": "DocumentStatusUpdated",
        "document_id": document_id,
        "status": status
    }

    event_queue.append(event)

    print("[WRITE] Document status updated successfully.")
    print("[WRITE] Event published.")

    return read_model[document_id]


def process_events():
    print("\n[EVENT] Event processing started.")
    time.sleep(3)

    while event_queue:
        event = event_queue.pop(0)
        document_id = event["document_id"]  
        read_model[document_id] = {
            "document_id": document_id,
            "file_name": event["file_name"],
            "status": event["status"],
            "embedding_version": event["embedding_version"]
        }

        print(f"[EVENT] Processed event for document: {document_id}")

def get_document_status(document_id):
    print("[QUERY] Fetching document status...")
    document = read_model.get(document_id)
    if document is None:
        return{
            "status": "NOT_FOUND",
        }
    return document


def get_documents_by_embedding_version(version):

    results = []

    for document in read_model.values():

        if document.get("embedding_version") == version:
            results.append(document)

    return results



print("===================================")
print("DAY 134 - CQRS DEMO")
print("===================================")

response = upload_document("DOC-001", "sales.pdf")
print("\nUpload response:")
print(response)


response = upload_document("DOC-002", "finance.pdf")
print("\nUpload response:")
print(response)

response = upload_document("DOC-003", "hr.pdf")
print("\nUpload response:")
print(response)



print("\nImmediately checking status:")

status = get_document_status("DOC-001")

print(status)

projection_thread = threading.Thread(
    target=process_events
)

projection_thread.start()
projection_thread.join()

print("\nChecking status again:")
update_document_status("DOC-001", "PROCESSED")
status = get_document_status("DOC-001")

print(status)

print("\nDocuments using embedding-v1:")

results = get_documents_by_embedding_version("v1")

for document in results:
    print(document)

