import pandas as pd
from deltalake import DeltaTable,write_deltalake

table_path = "learnings/data/day137_delta_table"

data = pd.DataFrame(
    [
        {
            "document_id": "DOC-001",
            "status": "UPLOADED",
            "version": 1
        },
        {
            "document_id": "DOC-002",
            "status": "UPLOADED",
            "version": 1
        }
    ]
)

updated_data = pd.DataFrame(
    [
        {
            "document_id": "DOC-001",
            "status": "PROCESSED",
            "version": 2
        },
        {
            "document_id": "DOC-002",
            "status": "UPLOADED",
            "version": 1
        },
        {
            "document_id": "DOC-003",
            "status": "UPLOADED",
            "version": 1
        }
    ]
)
write_deltalake(table_path, updated_data, mode="overwrite")

print("Delta table created.")

table = DeltaTable(table_path)
print("\nCurrent data:")
print(table.to_pandas())
print("\nDelta table history:")
print(table.history())