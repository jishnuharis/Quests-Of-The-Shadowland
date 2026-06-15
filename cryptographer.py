import base64
from fernet import Fernet

key = b'LEgh3Mkd0-WFJr0dLlKJ_hLvXP-Kdys8kx4JS2yKa9Q='


def encrypt(data):
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(str(data).encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()


def decrypt(encrypted_data):
    cipher_suite = Fernet(key)
    try:
        decrypted_data = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_data))
        return decrypted_data.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        raise


def overwrite_env(file_path, security_ey, new_value):
    with open(file_path, "r") as file:
        lines = file.readlines()

    for i in range(len(lines)):
        if lines[i].startswith(security_ey + "="):
            encrypted_new_value = encrypt(new_value)
            lines[i] = f"{security_ey}='{encrypted_new_value}'\n"
            break

    with open(file_path, "w") as file:
        file.writelines(lines)


overwrite_env(".env", "LEVEL", 1)
overwrite_env(".env", "MAX_LEVEL", 10)
overwrite_env(".env", "HIGH_SCORE", 0)

