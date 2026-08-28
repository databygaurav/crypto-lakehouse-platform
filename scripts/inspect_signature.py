from utils.signature import generate_signature

secret = "my_secret_key"
query = "timestamp=123456789"

signature = generate_signature(secret,query)

print(signature)