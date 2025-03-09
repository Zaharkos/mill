"""
Python wrapper of encryption engine
"""

import ctypes

class Engine:
    """
    Wraps encryption engine functional
    """

    __engine = None

    def __init__(self):
        """
        Creates encryption engine if it was not created yet
        """

        if Engine.__engine is not None:
            return

        Engine.__engine = ctypes.cdll.LoadLibrary("./backend/encryption/engine.so")

        Engine.__engine.generateRandomKey.argtypes = []
        Engine.__engine.generateRandomKey.restype = ctypes.c_void_p

        Engine.__engine.freeMemory.argtypes = [ctypes.c_void_p]
        Engine.__engine.freeMemory.restype = None

    def generate_random_key(self):
        """
        Generates random key for encryption/decryption

        Returns:
            str: key
        """

        result_ptr = Engine.__engine.generateRandomKey()

        random_key = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")

        Engine.__engine.freeMemory(result_ptr)

        return random_key


if __name__ == "__main__":
    for i in range(5):
        key = Engine().generate_random_key()
        print(f"Key {i + 1}: {key}")
