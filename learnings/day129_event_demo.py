from messaging.event_bus import event_bus, publish_event

import threading


def event_worker():

    while True:

        event = event_bus.get()

        print(
            f"[Consumer] Received: "
            f"{event['event_type']}"
        )

        print(
            f"[Consumer] Processing: "
            f"{event['document_id']}"
        )

        event_bus.task_done()


event = {
    "event_id": "EVT-001",
    "event_type": "DocumentIngestionCompleted",
    "job_id": "JOB-001",
    "document_id": "DOC-001"
}


worker = threading.Thread(
    target=event_worker,
    daemon=True
)

worker.start()

publish_event(event)

event_bus.join()