import hmac
import hashlib
import base64
import time
import json

class NFCHMAC:
    """HMAC signer/verifier for NFC data"""
    def __init__(self, secret: bytes):
        self.secret = secret

    def generate(self, data: str) -> str:
        mac = hmac.new(self.secret, data.encode(), hashlib.sha1).digest()
        return base64.urlsafe_b64encode(mac).decode()

    def verify(self, data: str, signature: str) -> bool:
        try:
            mac = base64.urlsafe_b64decode(signature)
            expected = hmac.new(self.secret, data.encode(), hashlib.sha1).digest()
            return hmac.compare_digest(mac, expected)
        except Exception:
            return False

if __name__ == "__main__":
    secret = b"SUPER_SECRET_KEY_32_BYTES"
    signer = NFCHMAC(secret)
    data = "966243980"

    ts = int(1770889117)
    payload_dict = {"uid": data, "ts": ts}
    data_str = json.dumps(payload_dict, separators=(",", ":"))
    payload_dict["hmac"] = signer.generate(data_str)
    payload_json = json.dumps(payload_dict, separators=(",", ":"))
    print(payload_json)