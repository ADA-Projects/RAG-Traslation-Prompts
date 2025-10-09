import re
from collections import Counter
from typing import List


def detect_stammer(source_sentence: str, translated_sentence: str) -> bool:
    """Detect stammering (non-natural repetition) in a translated sentence.

    Stammering refers to the non-natural repetition of text parts in machine
    translation output, resulting in awkward or nonsensical sentences.

    Args:
        source_sentence: The original source sentence
        translated_sentence: The translated sentence to analyze

    Returns:
        True if stammering is detected, False otherwise
    """
    # Normalize and tokenize
    trans_lower = translated_sentence.lower()
    words = trans_lower.split()

    if len(words) == 0:
        return False

    # Rule 1: Detect extreme character elongation (e.g., "soooooo...")
    # Look for characters repeated more than 5 times
    if re.search(r'(.)\1{5,}', trans_lower):
        return True

    # Rule 2: Consecutive identical words (for words longer than 2 chars to avoid "a a")
    for i in range(len(words) - 1):
        word = words[i].strip('.,!?;:')
        next_word = words[i + 1].strip('.,!?;:')
        if word == next_word and len(word) > 2:
            return True

    # Rule 3: Consecutive identical bigrams (phrase repetition)
    if len(words) >= 4:
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i + 1]}"
            bigrams.append(bigram)

        for i in range(len(bigrams) - 1):
            if bigrams[i] == bigrams[i + 1]:
                return True

    # Rule 4: Excessive word repetition compared to source
    # Count repetitions in both sentences
    source_words = source_sentence.lower().split()
    source_counter = Counter(w.strip('.,!?;:') for w in source_words if len(w.strip('.,!?;:')) > 2)
    trans_counter = Counter(w.strip('.,!?;:') for w in words if len(w.strip('.,!?;:')) > 2)

    # Check if translation has disproportionately more repetition
    # If a word appears much more often in translation than in source, it might be stammering
    for word, trans_count in trans_counter.items():
        source_count = source_counter.get(word, 0)

        # If word appears more than 3 times in translation and at least 3x more than source
        if trans_count > 3 and (source_count == 0 or trans_count >= source_count * 3):
            return True

    return False
