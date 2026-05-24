class ParserError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UnsupportedFileError(ParserError):
    pass

class CorruptedFileError(ParserError):
    pass