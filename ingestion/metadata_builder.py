class MetadataBuilder:

    def build(self, chunks):
        print("Building metadata")
        
        result = []
        for i, _ in enumerate(chunks):
            result.append({
                "chunk_id": i,
                "source": "LeavePolicy.pdf"
            })
        return result