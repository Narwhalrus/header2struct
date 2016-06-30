from ctypes import *

class PtrWrapper:
    def __init__(self, ptr):
        # This is of type c_void_p
        self.ptr = ptr

    def as_int32(self, idx = 0):
        return cast(self.ptr, POINTER(c_int))[idx]

    def as_uint32(self, idx = 0):
        return cast(self.ptr, POINTER(c_uint))[idx]

    def as_byte(self, idx = 0):
        return cast(self.ptr, POINTER(c_byte))[idx]

    def as_ubyte(self, idx = 0):
        return cast(self.ptr, POINTER(c_ubyte))[idx]

    def as_float32(self, idx = 0):
        return cast(self.ptr, POINTER(c_float))[idx]

    def to_int32(self, val, idx = 0):
        cast(self.ptr, POINTER(c_int))[idx] = val

    def to_uint32(self, val, idx = 0):
        cast(self.ptr, POINTER(c_uint))[idx] = val
    
    def to_byte(self, val, idx = 0):
        cast(self.ptr, POINTER(c_byte))[idx] = val
    
    def to_ubyte(self, val, idx = 0):
        cast(self.ptr, POINTER(c_ubyte))[idx] = val

    def to_float32(self, val, idx = 0):
        cast(self.ptr, POINTER(c_float))[idx] = val

class MemSect:
    def __init__(self, base_ptr, size):
        self.base = base_ptr
        self.size = size

    def __getitem__(self, index):
        if index > self.size:
            raise IndexError 
        return PtrWrapper(self.base + index)
