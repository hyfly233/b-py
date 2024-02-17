from mem0 import Memory

memory = Memory()

messages = [
    {"role": "user", "content": "我喜欢早上喝咖啡然后去散步"}
]
result = memory.add(messages, user_id="alice", metadata={"category": "preferences"})
