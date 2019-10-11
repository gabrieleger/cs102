def encrypt_caesar(plaintext: str) -> str:
    """
    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext=''
    for letter in plaintext:
        if letter in 'xyzXYZ':
            if letter=='x':
                ciphertext += 'a'
            if letter=='y':
                ciphertext += 'b'
            if letter=='z':
                ciphertext += 'c'
            if letter=='X':
                ciphertext += 'A'
            if letter=='Y':
                ciphertext += 'B'
            if letter=='Z':
                ciphertext += 'C'
        elif letter.isalpha() :
            ciphertext += chr(ord(letter)+3)
        else:
            ciphertext+=letter 
    return ciphertext


def decrypt_caesar(ciphertext: str) -> str:
    """
    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext=''
    for letter in ciphertext:
        if letter in 'abcABC':
            if letter=='a':
                plaintext += 'x'
            if letter=='b':
                plaintext += 'y'
            if letter=='c':
                plaintext += 'z'
            if letter=='A':
                plaintext += 'X'
            if letter=='B':
                plaintext += 'Y'
            if letter=='C':
                plaintext += 'Z'
        elif letter.isalpha() :
            plaintext += chr(ord(letter)-3)
        else:
            plaintext+=letter 
    return plaintext