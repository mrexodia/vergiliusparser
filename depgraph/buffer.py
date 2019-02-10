
class BufferFull(Exception):
    def __str__(self):
        return "buffer full"

class BufferEmpty(Exception):
    def __str__(self):
        return "buffer empty"

class RingIndex(object):

    def __init__(self, size, start=0):
        self.index = start
        self.size = size

    def incr(self):
        self.index += 1
        if self.index == self.size:
            self.index = 0
        return self.index

    @property
    def next(self):
        if self.index == self.size - 1:
            return 0
        return self.index + 1

    @property
    def prev(self):
        if self.index == 0:
            return self.size - 1
        return self.index - 1

    def __repr__(self):
        return "RingIndex[size={}, index={}]".format(self.size, self.index)

class FIFO(object):

    def __init__(self, size):
        self.size = size
        self._buffer = [None for _ in range(size + 1)]

        # Convention:
        # Ring buffer is full when the write index is just before the read index
        # Ring buffer is empty when the write and read indices are equal
        # Therefore, there is always at least one empty slot in the array, even
        # when the buffer is full.
        self._write_offset = RingIndex(size + 1)
        self._read_offset = RingIndex(size + 1)

    def push(self, item):
        if self._write_offset.next == self._read_offset.index:
            raise BufferFull

        self._buffer[self._write_offset.index] = item
        self._write_offset.incr()

    def pop(self):
        if self._write_offset.index == self._read_offset.index:
            raise BufferEmpty

        retval = self._buffer[self._read_offset.index]
        self._read_offset.incr()
        return retval

