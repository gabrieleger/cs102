def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext=''
    ind = 0
    keyword=keyword.lower()
    for letter in plaintext:
        if letter.isalpha():
            shift=ord(keyword[ind%len(keyword)]) - 97
            if letter.islower():
                new_letter = chr((ord(letter) - 97 + shift) % 26 + 97)
            else:
                new_letter = chr((ord(letter) - 65 + shift) % 26 + 65)
            ciphertext += new_letter
        else:
            ciphertext += letter
        ind+=1 
    
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext=''
    ind = 0
    keyword=keyword.lower()
    for letter in ciphertext:
        if letter.isalpha():
            shift=ord(keyword[ind%len(keyword)]) - 97
            if letter.islower():
                new_letter = chr((ord(letter) - 97 - shift) % 26 + 97)
            else:
                new_letter = chr((ord(letter) - 65 - shift) % 26 + 65)
            plaintext += new_letter
        else:
            plaintext += letter
        ind+=1 

    return plaintext