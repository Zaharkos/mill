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

        Engine.__engine.encode.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        Engine.__engine.encode.restype = ctypes.c_void_p

        Engine.__engine.decode.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        Engine.__engine.decode.restype = ctypes.c_void_p

        Engine.__engine.generateRandomKey.argtypes = []
        Engine.__engine.generateRandomKey.restype = ctypes.c_void_p

        Engine.__engine.freeMemory.argtypes = [ctypes.c_void_p]
        Engine.__engine.freeMemory.restype = None

    def encode(self, string_data, universal_key):
        """
        Encodes given data by key

        Args:
            string_data (str): data to encode
            universal_key (str): encode/decode key

        Returns:
            str: encoded data
        """

        result_ptr = Engine.__engine.encode(
            string_data.encode("utf-8"),
            universal_key.encode("utf-8")
        )

        random_key = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")

        Engine.__engine.freeMemory(result_ptr)

        return random_key

    def decode(self, string_data, universal_key):
        """
        Decodes given data by key

        Args:
            string_data (str): data to encode
            universal_key (str): encode/decode key

        Returns:
            str: encoded data
        """

        result_ptr = Engine.__engine.decode(
            string_data.encode("utf-8"),
            universal_key.encode("utf-8")
        )

        random_key = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")

        Engine.__engine.freeMemory(result_ptr)

        return random_key

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
    key = Engine().generate_random_key()
    print(f"Key: {key}")

    encoded = Engine().encode("qwerty", key)
    print(f"Encoded: {encoded}")

    decoded = Engine().decode(encoded, key)
    print(f"Decoded: {decoded}")
