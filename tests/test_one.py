import unittest
import hashlib
from ecdsa import SigningKey, NIST256p, NIST384p
from ace_custom.edhoc.protocol import EdhocClient, EdhocServer, OscoreContext
from ace_custom.edhoc.oscore_context import bxor
from ace_custom.edhoc.util import ecdsa_key_to_cose, ecdsa_cose_to_key


class TestEdhoc(unittest.TestCase):


    def test_xor(self):
        a = bytes.fromhex("1234")
        b = bytes.fromhex("5678")

        assert (bxor(a, b) == bytes.fromhex("444C"))


if __name__ == '__main__':
    unittest.main()
