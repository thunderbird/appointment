class UnexpectedBehaviourWarning(RuntimeWarning):
    def __init__(self, message: str, info: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.info = info
