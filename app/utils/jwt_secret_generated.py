import secrets

def generate_jwt_secret_key(length=32):
    """Generate a secure random JWT secret key."""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    jwt_secret_key = generate_jwt_secret_key()
    print("Generated JWT Secret Key:", jwt_secret_key)