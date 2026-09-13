import base64
import os

with open(r"assets/monkey/monkey_volume_transparent.png", "rb") as f:
    data = f.read()

b64 = base64.b64encode(data).decode('ascii')
print("Base64 length:", len(b64))

# Let's verify we can decode and slice it cleanly
import io
from PIL import Image

decoded = Image.open(io.BytesIO(base64.b64decode(b64)))
print("Decoded image size:", decoded.size)
