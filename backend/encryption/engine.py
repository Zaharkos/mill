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

        Engine.__engine = ctypes.cdll.LoadLibrary("../encryption/engine.so")

        Engine.__engine.encode.argtypes = [ctypes.c_char_p, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_char_p]
        Engine.__engine.encode.restype = ctypes.c_uint64

        Engine.__engine.decode.argtypes = [ctypes.c_char_p, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_char_p]
        Engine.__engine.decode.restype = ctypes.c_uint64

        Engine.__engine.generateRandomKey.argtypes = [ctypes.c_char_p]
        Engine.__engine.generateRandomKey.restype = ctypes.c_uint64

        Engine.__engine.predictEncodedSize.argtypes = [ctypes.c_uint64]
        Engine.__engine.predictEncodedSize.restype = ctypes.c_uint64

    def encode(self, byte_data, universal_key):
        """
        Encodes given data by key

        Args:
            byte_data (bytes): data to encode
            universal_key (str): encode/decode key

        Returns:
            str: encoded data
        """

        res_buffer = ctypes.create_string_buffer(Engine.__engine.predictEncodedSize(len(byte_data)))

        encoded_data_size = Engine.__engine.encode(
            byte_data,
            len(byte_data),
            universal_key,
            res_buffer
        )

        return res_buffer.raw[:encoded_data_size]

    def decode(self, byte_data, universal_key):
        """
        Decodes given data by key

        Args:
            byte_data (bytes): data to encode
            universal_key (str): encode/decode key

        Returns:
            str: encoded data
        """

        res_buffer = ctypes.create_string_buffer(len(byte_data))

        decoded_data_size = Engine.__engine.decode(
            byte_data,
            len(byte_data),
            universal_key,
            res_buffer
        )

        return res_buffer[:decoded_data_size]

    def generate_random_key(self):
        """
        Generates random key for encryption/decryption

        Returns:
            str: key
        """

        res_buffer = ctypes.create_string_buffer(Engine.__engine.getMaxKeySize())

        key_real_size = Engine.__engine.generateRandomKey(res_buffer)

        return res_buffer.raw[:key_real_size]
