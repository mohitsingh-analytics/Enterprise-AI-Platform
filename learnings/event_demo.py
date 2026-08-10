events=[]

def publish_event(event):
    events.append(event)

def ingest_document(file_name):
    print(f"Received document: {file_name}")
    print("loading document...")
    print("creating chunks...")
    print("generating embeddings...")
    print("saving to vector DB...")

    publish_event({
        "event_type": "document_ingested", 
        "document_name": file_name,
    })
    print("Ingestion completed.")

def notification_service(event):
    if event["event_type"] == "document_ingested":
        print(f"Notification: Document '{event['document_name']}' has been ingested successfully.")

def audit_service(event):
    if event["event_type"] == "document_ingested":
        print(f"Notification: Document '{event['document_name']}' has been recorded for Audit.")


ingest_document("hello.pdf")

for event in events:
    notification_service(event)
    audit_service(event)
print(events)