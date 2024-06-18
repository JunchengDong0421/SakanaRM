import random
import string


def random_filename(length=10, ext="pdf"):
    pool = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(pool, k=length))
    return f"{random_string}.{ext}"
