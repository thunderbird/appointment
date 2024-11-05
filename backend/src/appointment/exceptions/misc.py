class UnexpectedBehaviourWarning(RuntimeWarning):
    def __init__(self, message: str, info: dict):
        self.message = message
        self.info = info
