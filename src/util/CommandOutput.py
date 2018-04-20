class CommandOutput:
    def __init__(self, success, output, error):
        self.success = success
        self.output = output
        self.error = error

    def __str__(self):
        return f'success={self.success}, output={self.output}, error={self.error}'
