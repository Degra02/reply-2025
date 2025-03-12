import hashlib
from datetime import datetime

def xor_bytes(a, b):
    """XOR two byte sequences (up to the length of the shorter one)."""
    return bytes(x ^ y for x, y in zip(a, b))

def repeat_mask(mask, length):
    """Repeat the 16-byte mask to cover 'length' bytes."""
    repeated = (mask * ((length // len(mask)) + 1))[:length]
    return repeated

def compute_mask(timestamp_str):
    """
    Given a timestamp string (e.g. "2025-03-10 09:50:07.974000"),
    re-compute the MD5 mask as done in the challenge.
    """
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
    ts_float = round(dt.timestamp(), 3)
    ts_int = int(ts_float * 1000)
    ts_bytes = ts_int.to_bytes(16, byteorder='big')
    return hashlib.md5(ts_bytes).digest()

def decrypt_flag(timestamp1, ciphertext1_hex, timestamp2, ciphertext2_hex, known_plaintext):
    """
    Given:
      - timestamp1 and ciphertext1 (the known plaintext message) 
      - timestamp2 and ciphertext2 (the flag message)
      - known_plaintext: the plaintext corresponding to message 1
    Returns the recovered flag (for the overlapping portion).
    """
    # Convert hex strings to bytes.
    c1 = bytes.fromhex(ciphertext1_hex)
    c2 = bytes.fromhex(ciphertext2_hex)
    
    # Work on the overlapping portion.
    common_length = min(len(c1), len(c2))
    c1 = c1[:common_length]
    c2 = c2[:common_length]
    
    # Compute the MD5 masks for each message.
    mask1 = compute_mask(timestamp1)
    mask2 = compute_mask(timestamp2)
    
    # Repeat the masks to cover the entire length.
    mask1_rep = repeat_mask(mask1, common_length)
    mask2_rep = repeat_mask(mask2, common_length)
    
    # Compute combined mask difference.
    mask_diff = xor_bytes(mask1_rep, mask2_rep)
    
    # XOR the two ciphertexts.
    xor_c = xor_bytes(c1, c2)
    # (C1 ⊕ C2) = (P1 ⊕ P2 ⊕ (mask1 ⊕ mask2)).
    # Cancel out the extra mask by XORing with mask_diff:
    p1_xor_p2 = xor_bytes(xor_c, mask_diff)
    
    # Prepare known plaintext bytes.
    p1_bytes = known_plaintext.encode()
    if len(p1_bytes) < common_length:
        print("Warning: Known plaintext is shorter than the overlapping ciphertext length.")
        # We'll use only the known portion. Extra bytes of the flag remain unrecovered.
        p1_bytes = p1_bytes
    else:
        p1_bytes = p1_bytes[:common_length]
    
    # Recover the flag portion: P2 = P1 ⊕ (P1 ⊕ P2).
    recovered_flag_bytes = xor_bytes(p1_bytes, p1_xor_p2)
    
    return recovered_flag_bytes.decode(errors="ignore")

if __name__ == "__main__":
    print("Enter data for the first message (known plaintext):")
    timestamp1 = input("Timestamp (e.g. 2025-03-10 09:50:07.974000): ").strip()
    ciphertext1_hex = input("Ciphertext (hex): ").strip()
    
    print("\nEnter data for the second message (flag):")
    timestamp2 = input("Timestamp (e.g. 2025-03-10 09:50:10.975000): ").strip()
    ciphertext2_hex = input("Ciphertext (hex): ").strip()
    
    known_plaintext = input("\nEnter the known plaintext (message 1): ").strip()
    
    flag = decrypt_flag(timestamp1, ciphertext1_hex, timestamp2, ciphertext2_hex, known_plaintext)
    print("\n[+] Recovered Flag (overlapping portion):")
    print(flag)

