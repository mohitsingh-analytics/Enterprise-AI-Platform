from queue import Queue

event_bus = Queue()


def publish_event(event):
    event_bus.put(event)

    print(
        f"[Event Bus] Published: "
        f"{event['event_type']} | "
        f"{event['event_id']}"
    )