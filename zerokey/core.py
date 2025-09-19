import os, base64, blake3, kyber_py.kyber as kyber
from argon2.low_level import hash_secret_raw, Type
from nacl.secret import SecretBox

class ZKChannel:
    def __init__(self, password: str):
        self.pwd = password.encode()

    # ---------- ZKP-derived key ----------
    def _zk_key(self, salt: bytes) -> bytes:
        return hash_secret_raw(self.pwd, salt, time_cost=3,
                               memory_cost=2**16, hash_len=32, type=Type.ID)

    # ---------- client hello ----------
    def client_hello(self, server_kyber_pk: bytes):
        salt = os.urandom(16)
        sk = self._zk_key(salt)
        kyber_sk, kyber_pk = kyber.Kyber512.keypair()
        challenge = blake3(sk + kyber_pk).digest()
        hello = {"salt": base64.b64encode(salt).decode(),
                 "pk": base64.b64encode(kyber_pk).decode(),
                 "chal": base64.b64encode(challenge).decode()}
        return hello, kyber_sk

    # ---------- server response ----------
    def server_response(self, hello: dict, server_kyber_sk: bytes):
        salt = base64.b64decode(hello["salt"])
        pk = base64.b64decode(hello["pk"])
        chal = base64.b64decode(hello["chal"])
        sk = self._zk_key(salt)
        if blake3(sk + pk).digest() != chal:
            raise ValueError("ZKP fail")
        cipher, shared = kyber.Kyber512.enc(pk)
        box = SecretBox(blake3(shared).digest())
        token = box.encrypt(b"AUTH_OK", os.urandom(24))
        return {"cipher": base64.b64encode(cipher).decode(),
                "token": base64.b64encode(token).decode()}, shared

    # ---------- client finish ----------
    def client_finish(self, rsp: dict, client_kyber_sk: bytes):
        cipher = base64.b64decode(rsp["cipher"])
        shared = kyber.Kyber512.dec(cipher, client_kyber_sk)
        box = SecretBox(blake3(shared).digest())
        token = base64.b64decode(rsp["token"])
        if box.decrypt(token) != b"AUTH_OK":
            raise ValueError("Server auth fail")
        return shared   # 32-byte session key

    # ---------- ChaCha20-Poly1305 ----------
    def make_box(self, key32: bytes) -> SecretBox:
        return SecretBox(key32)
