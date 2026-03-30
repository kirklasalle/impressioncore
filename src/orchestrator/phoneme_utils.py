
import logging

logger = logging.getLogger(__name__)

# Basic Arpabet mapping to index (0-255) for 256-vocab phoneme processing
ARPABET_PHONEMES = [
    "AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH", "EH", "ER", "EY", "F", "G",
    "HH", "IH", "IY", "JH", "K", "L", "M", "N", "NG", "OW", "OY", "P", "R", "S", "SH", "T",
    "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH", " "
]

PHONEME_TO_ID = {p: i + 1 for i, p in enumerate(ARPABET_PHONEMES)}
ID_TO_PHONEME = {i + 1: p for i, p in enumerate(ARPABET_PHONEMES)}

# Placeholder for a real G2P implementation
# In a full system, this would use g2p_en or a similar library.
def text_to_phoneme_ids(text: str, max_length: int = 128) -> list:
    """
    Converts text to a sequence of phoneme IDs.
    Currently uses a simplified character-to-phoneme mapping for simulation.
    """
    phonemes = []
    # Simplified: map vowels and consonants roughly
    vowels = "aeiouAEIOU"
    for char in text.upper():
        if char == " ":
            phonemes.append(PHONEME_TO_ID[" "])
        elif char in vowels:
            phonemes.append(PHONEME_TO_ID["AH"]) # Default vowel
        elif char.isalpha():
            phonemes.append(PHONEME_TO_ID["S"])  # Default consonant

    # Pad or truncate
    phonemes = phonemes[:max_length]
    return phonemes

def phoneme_ids_to_text(ids: list) -> str:
    """
    Decodes phoneme IDs back to a (rough) string representation.
    """
    return "".join([ID_TO_PHONEME.get(i, "?") for i in ids])

class PhonemeProcessor:
    """
    Utility class for system-wide phoneme handling.
    """
    def __init__(self, vocab_size: int = 256):
        self.vocab_size = vocab_size

    def encode(self, text: str):
        return text_to_phoneme_ids(text)

    def decode(self, ids: list):
        return phoneme_ids_to_text(ids)
