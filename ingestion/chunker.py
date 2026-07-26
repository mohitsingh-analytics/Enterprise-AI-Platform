class Chunker:

    def chunk(self, text):

        print("Chunking")

        return [
            text[:20],
            text[20:]
        ]