import ctypes

class Engine:
    __engine = None

    def __init__(self):
        if Engine.__engine is None:
            Engine.__engine = ctypes.cdll.LoadLibrary("./backend/encryption/engine.so")

            Engine.__engine.encode.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            Engine.__engine.encode.restype = ctypes.c_void_p

            Engine.__engine.decode.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            Engine.__engine.decode.restype = ctypes.c_void_p

            Engine.__engine.getRandomKey.argtypes = []
            Engine.__engine.getRandomKey.restype = ctypes.c_void_p

            Engine.__engine.freeMemory.argtypes = [ctypes.c_void_p]
            Engine.__engine.freeMemory.restype = None

    def encode(self, string_data, string_key):
        result_ptr = Engine.__engine.encode(
            ctypes.cast(ctypes.c_char_p(string_data.encode("utf-8")), ctypes.c_void_p),
            ctypes.cast(ctypes.c_char_p(string_key.encode("utf-8")), ctypes.c_void_p)
        )

        encoded_data = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")

        Engine.__engine.freeMemory(result_ptr)

        return encoded_data

    def decode(self, string_encoded, string_key):
        result_ptr = Engine.__engine.decode(
            ctypes.cast(ctypes.c_char_p(string_encoded.encode("utf-8")), ctypes.c_void_p),
            ctypes.cast(ctypes.c_char_p(string_key.encode("utf-8")), ctypes.c_void_p)
        )

        decoded_data = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")

        Engine.__engine.freeMemory(result_ptr)

        return decoded_data

    def get_random_key(self):
        result_ptr = Engine.__engine.getRandomKey()

        random_key = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")

        Engine.__engine.freeMemory(result_ptr)

        return random_key

key = Engine().get_random_key()
print(f"Key: {key}")
print(Engine().encode("qwerty", key))
print(Engine().decode("qwerty", key))
