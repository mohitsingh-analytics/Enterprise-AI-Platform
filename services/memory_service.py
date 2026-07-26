import threading
from collections import defaultdict

class MemoryService:
    def __init__(self):
        # Keeps track of conversations by session_id
        self._conversations = defaultdict(list)
        print("*********MemoryService created:*********", id(self))

    
    def add_message(self, session_id: str, response_:str,query: str, context: str):
    
        # 1. Combine your context and query into one clean text string immediately
        
        user_query = f"Context:\n{context}\n\nQuestion:\n{query}"
        self._conversations[session_id].append({
            "role": "user",
            "content": user_query
        })
        
        
          
        self._conversations[session_id].append({
            "role": "assistant",
            "content": response_
        })
        
        # 2. Add it to our session list using Claude's required keys
        
        print("*********conversation created:*********",self._conversations)
        # 3. Use list slicing to instantly pull up to the last 3 items
        # No for loops needed! Python handles it automatically.
        return self._conversations[session_id]
    
    def get_history(self, session_id: str):   
        return self._conversations.get(session_id, [])
    
    def clear_history(self):
        with self._lock:  # Fixed: changed self.lock to self._lock
            self._conversations.clear()

#memory service comment to check git