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

    # Rule 2: Consecutive identical words (3+ times indicates stammering)
    # Allows natural doubles like "bye bye" but flags clear errors
    # Also check source to avoid false positives on legitimate repetition
    source_words = source_sentence.lower().split()

    i = 0
    while i < len(words) - 2:
        word = words[i].strip('.,!?;:')
        if len(word) <= 2:
            i += 1
            continue

        # Check if word repeats 3+ times consecutively in translation
        if (words[i + 1].strip('.,!?;:') == word and
            words[i + 2].strip('.,!?;:') == word):

            # Check if source also has 3+ consecutive repetitions (any word)
            # If source has similar pattern, translation might be legitimate
            source_has_repetition = False
            for j in range(len(source_words) - 2):
                source_word = source_words[j].strip('.,!?;:')
                if len(source_word) > 2:
                    if (source_words[j + 1].strip('.,!?;:') == source_word and
                        source_words[j + 2].strip('.,!?;:') == source_word):
                        source_has_repetition = True
                        break

            # Only flag as stammering if source doesn't have similar repetition
            if not source_has_repetition:
                return True
        i += 1

    # Rule 3: Consecutive identical bigrams (phrase repetition)
    # Also check source to avoid false positives on legitimate repetition
    if len(words) >= 4:
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i + 1]}"
            bigrams.append(bigram)

        for i in range(len(bigrams) - 1):
            if bigrams[i] == bigrams[i + 1]:
                # Check if source also has consecutive identical bigrams
                if len(source_words) >= 4:
                    source_bigrams = []
                    for j in range(len(source_words) - 1):
                        source_bigram = f"{source_words[j]} {source_words[j + 1]}"
                        source_bigrams.append(source_bigram)

                    source_has_bigram_repetition = False
                    for j in range(len(source_bigrams) - 1):
                        if source_bigrams[j] == source_bigrams[j + 1]:
                            source_has_bigram_repetition = True
                            break

                    # Only flag if source doesn't have similar pattern
                    if not source_has_bigram_repetition:
                        return True
                else:
                    # Source too short, flag the translation bigram repetition
                    return True
                break  # Only check first occurrence

    # Rule 4: Excessive word repetition compared to source
    # Count repetitions in both sentences
    source_words = source_sentence.lower().split()
    source_counter = Counter(w.strip('.,!?;:') for w in source_words if len(w.strip('.,!?;:')) > 2)
    trans_counter = Counter(w.strip('.,!?;:') for w in words if len(w.strip('.,!?;:')) > 2)

    # Find the maximum repetition count in source (language-agnostic approach)
    # We compare repetition patterns, not literal words across languages
    source_max_count = max(source_counter.values()) if source_counter else 0

    # Check if translation has disproportionately more repetition than source
    # Compare: "Does ANY word in translation repeat excessively MORE than the
    # MOST repeated word in source?"
    for word, trans_count in trans_counter.items():
        # Flag as stammering if:
        # 1. Word appears more than 3 times in translation (absolute threshold)
        # 2. It appears at least 3x more than the most repeated word in source
        if trans_count > 3 and trans_count >= 3 * source_max_count:
            return True

    return False
