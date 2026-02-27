from typing import List
from facebook import FacebookTool

class AccountPool:
    def __init__(self, cookies: List[str]):
        self._pool = [FacebookTool(c) for c in cookies]
        self._index = 0
    
    @property
    def current(self) -> FacebookTool:
        return self._pool[self._index]

    @property
    def next(self) -> FacebookTool:
        self._index = (self._index + 1) % len(self._pool)
        return self.current
    def __len__(self) -> int:
        return len(self._pool)

    def __getitem__(self, index: int) -> FacebookTool:
        return self._pool[index]

    def __iter__(self):
        return self