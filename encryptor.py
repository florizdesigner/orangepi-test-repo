import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


class NFCSigner:
    def __init__(self, private_key_path=None, public_key_path=None):
        self.private_key = None
        self.public_key = None

        if private_key_path:
            with open(private_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )

        if public_key_path:
            with open(public_key_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(f.read())

    def sign(self, data: str) -> str:
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.urlsafe_b64encode(signature).decode()

    def verify(self, data: str, signature: str) -> bool:
        try:
            self.public_key.verify(
                base64.urlsafe_b64decode(signature),
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
