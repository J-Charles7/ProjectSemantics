import ctypes

def int32_to_uint32(i):
    return ctypes.c_uint32(i).value

maVar = int (-3)
print(maVar)
print (int32_to_uint32(maVar))