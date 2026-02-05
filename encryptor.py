import hmac
import hashlib
import base64

class NFCHMAC:
    """HMAC signer/verifier for NFC data"""
    def __init__(self, secret: bytes):
        self.secret = secret

    def generate(self, data: str) -> str:
        mac = hmac.new(self.secret, data.encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(mac).decode()

    def verify(self, data: str, signature: str) -> bool:
        try:
            mac = base64.urlsafe_b64decode(signature)
            expected = hmac.new(self.secret, data.encode(), hashlib.sha256).digest()
            return hmac.compare_digest(mac, expected)
        except Exception:
            return False
