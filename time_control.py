class TimeControl:
    # Could be Python 3.7 @dataclass
    # Or Python 3.7 namedtuple with defaults
    
    def __init__(self, time: int, increment: int = 0, delay: int = 0) -> None:
        self.time = time
        self.increment = increment
        self.delay = delay
