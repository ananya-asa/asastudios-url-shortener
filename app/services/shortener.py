ALPHABET="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    if num==0:
        return ALPHABET[0]

    result=""
    while num>0:
        remainder=num%62
        result=ALPHABET[remainder]+result
        num=num//62
    return result
