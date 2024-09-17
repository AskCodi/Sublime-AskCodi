from json.decoder import JSONDecodeError
from typing import List, Dict, Iterator, Any, Optional

class Cache():
    def __init__(self) -> None:
        self.history = []

    def get_cache(self) -> List[Dict[str, str]]:
        return self.history


    def append_to_cache(self, cache_list: List[Dict[str, str]]):
        for item in cache_list:
            self.history.append(item)

    def clear_cache(self):
        self.history = []
