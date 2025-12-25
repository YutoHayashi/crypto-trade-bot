from collections import deque


class DataStore:
    """
    A service that provides a buffer to store data with a maximum size.
    When the buffer reaches its maximum size, the oldest data is discarded.
    """
    max_size: int
    _buffer: deque
    
    def append(self, data) -> None:
        """
        Appends data to the buffer. If the buffer exceeds its maximum size, the oldest data is removed.
        :param data: The data to be appended to the buffer.
        """
        self._buffer.append(data)
    
    def get_data(self):
        """
        Returns a copy of the current data in the buffer.
        :return: A list containing the data in the buffer.
        """
        return list(self._buffer)
    
    def __len__(self):
        return len(self._buffer)
    
    def __init__(self,
                 max_size: int):
        self.max_size = int(max_size)
        self._buffer = deque(maxlen=self.max_size)