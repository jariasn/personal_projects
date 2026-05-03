class Request:
    def __init__(self, model = "llama3", stream = False):
        self.model = model
        self.stream = stream

    def request(message):
        json_request = {
            "model": self.model,
            "functions": o,
            "messages": message,
            "stream": self.stream,
        }