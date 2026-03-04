import os
import json
import re

# 1. Pywikibot கட்டமைப்பு கோப்பை உருவாக்குதல்
with open('user-config.py', 'w') as f:
    f.write("family = 'wikisource'\n")
    f.write("mylang = 'ta'\n")
    f.write("usernames['wikisource']['ta'] = u'Neyakkoo_Bot'\n")

import pywikibot
from pywikibot.page import Page # Explicitly import Page

GRANTHA_CHARS = {'ஜ', 'ஷ', 'ஸ', 'ஹ'}

# Define VALID_INITIAL_TAMIL_CHARS as per previous steps
VALID_INITIAL_TAMIL_CHARS = set()

# 1. Add all 12 Tamil vowels (உயிரெழுத்துக்கள்)
vowels = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ']
VALID_INITIAL_TAMIL_CHARS.update(vowels)

# 2. உயிர்மெய் எழுத்துக்கள் (vowel-consonant combinations) for க, ச, த, ந, ப, ம

# Base consonants for full 12 combinations
full_comb_consonants = ['க', 'ச', 'த', 'ந', 'ப', 'ம']

# Vowel modifiers for 12 combinations
vowel_modifiers = [
    '',   # அ
    'ா',  # ஆ
    'ி',  # இ
    'ீ',  # ஈ
    'ு',  # உ
    'ூ',  # ஊ
    'ெ',  # எ
    'ே',  # ஏ
    'ை',  # ஐ
    'ொ',  # ஒ
    'ோ',  # ஓ
    'ௌ'   # ஔ
]

# Mapping for special uyirmey forms (உ, ஊ for சில எழுத்துகள்)
special_u_forms = {
    'கு': 'கு',
    'சு': 'சு',
    'டு': 'டு',
    'து': 'து',
    'நு': 'நு',
    'பு': 'பு',
    'மு': 'மு',
    'யு': 'யு',
    'ரு': 'ரு',
    'லு': 'லு',
    'வு': 'வு',
    'ழு': 'ழு',
    'ளு': 'ளு',
    'று': 'று',
    'னு': 'னு'
}
special_uu_forms = {
    'கூ': 'கூ',
    'சூ': 'சூ',
    'டூ': 'டூ',
    'தூ': 'தூ',
    'நூ': 'நூ',
    'பூ': 'பூ',
    'மூ': 'மூ',
    'யூ': 'யூ',
    'ரூ': 'ரூ',
    'லூ': 'லூ',
    'வூ': 'வூ',
    'ழூ': 'ழூ',
    'ளூ': 'ளூ',
    'றூ': 'றூ',
    'னூ': 'னூ'
}

# Generate full 12 combinations for 'க', 'ச', 'த', 'ந', 'ப', 'ம'
for consonant_base in full_comb_consonants:
    for i, modifier in enumerate(vowel_modifiers):
        # For 'ு' and 'ூ', prefer specific forms if they exist (though mostly for other consonants)
        if modifier == 'ு':
            char = special_u_forms.get(consonant_base + modifier, consonant_base + modifier)
        elif modifier == 'ூ':
            char = special_uu_forms.get(consonant_base + modifier, consonant_base + modifier)
        else:
            char = consonant_base + modifier
        VALID_INITIAL_TAMIL_CHARS.add(char)

# 3. ய series: ய, யா, யு, யூ, யோ, யௌ
y_series = ['ய', 'யா', 'யு', 'யூ', 'யோ', 'யௌ']
VALID_INITIAL_TAMIL_CHARS.update(y_series)

# 4. வ series: வ, வா, வி, வீ, வெ, வே, வை, வொ, வோ, வௌ (excluding வு, வூ)
v_series = ['வ', 'வா', 'வி', 'வீ', 'வெ', 'வே', 'வை', 'வொ', 'வோ', 'வௌ']
VALID_INITIAL_TAMIL_CHARS.update(v_series)

# 5. ஞ series: ஞ, ஞா, ஞெ, ஞோ
gn_series = ['ஞ', 'ஞா', 'ஞெ', 'ஞோ']
VALID_INITIAL_TAMIL_CHARS.update(gn_series)

# 6. ங series: only ங
VALID_INITIAL_TAMIL_CHARS.add('ங')

ORAEZHUTHU_ORUMOZI = {
    'ஆ', 'ஈ', 'ஊ', 'ஏ', 'ஐ', 'ஓ', 'கா', 'கு', 'கை', 'கோ', 'சா', 'சி', 'சே', 'சோ',
    'தா', 'தீ', 'தூ', 'தே', 'நை', 'நோ', 'பா', 'பூ', 'பே', 'பை', 'போ', 'மா', 'மீ',
    'மு', 'மே', 'மை', 'மோ', 'யா', 'வா', 'வீ', 'வே', 'வை', 'நொ', 'து', 'த', 'க', 'ம',
    'அ', 'இ', 'எ'
}

# Define VALID_WORD_ENDINGS
VALID_WORD_ENDINGS = set()
VALID_WORD_ENDINGS.update(vowels) # All 12 Tamil vowels

# Pure consonants from மெல்லினம் and இடையினம்
pure_consonants_endings = ['ங்', 'ஞ்', 'ண்', 'ந்', 'ம்', 'ன்', 'ய்', 'ர்', 'ல்', 'வ்', 'ழ்', 'ள்']
VALID_WORD_ENDINGS.update(pure_consonants_endings)

# குற்றியலுகரம் forms
kutriyalugaram_forms = ['கு', 'சு', 'டு', 'து', 'பு', 'று']
VALID_WORD_ENDINGS.update(kutriyalugaram_forms)

def clean_tamil_word(word_to_clean):
    """
    Cleans a Tamil word by removing numbers (Tamil and Arabic) and invalid final hard consonants
    based on 'மொழியிறுதி எழுத்துகள்' rules and user's 'இந்தக்' example.
    """
    # 1. Remove Tamil digits (\u0be6-\u0bef) and Arabic digits (0-9)
    # This will remove any numbers from anywhere in the word.
    cleaned_word = re.sub(r'[\u0be6-\u0bef0-9]', '', word_to_clean)

    # 2. Remove invalid final hard consonants (வல்லின மெய்யெழுத்துகள்)
    # These are unicode representations of (க,ச,ட,த,ப,ற) + புள்ளி (்)
    invalid_final_consonants_unicodes = [
        'க\u0bcd',  # க்
        'ச\u0bcd',  # ச்
        'ட\u0bcd',  # ட்
        'த\u0bcd',  # த்
        'ப\u0bcd',  # ப்
        'ற\u0bcd'   # ற்
    ]

    for inv_consonant in invalid_final_consonants_unicodes:
        if cleaned_word.endswith(inv_consonant):
            # Remove the invalid final consonant (e.g., 'இந்தக்' -> 'இந்த')
            cleaned_word = cleaned_word[:-len(inv_consonant)]
            break # Only one such consonant can be at the very end

    return cleaned_word # Return the cleaned word

def check_tamil_phonotactics(word):
    """
    Checks a cleaned Tamil word for common non-native Tamil consonant cluster patterns.
    Returns True if a violation is detected, False otherwise.
    """
    if not word:
        return False # Empty word is not a violation

    # 1. Check for `உடனிலை மெய்ம்மயக்கம்` (identical consonant clusters - specific invalid geminations)
    # Specifically flag ட் ட் or ற் ற் as pure consonants.
    # `([டற]்)(\1)` checks for 'ட்' followed by '்' and then the same 'ட்' followed by '்'
    # or 'ற்' followed by '்' and then the same 'ற்' followed by '்'.
    if re.search(r'([டற]\u0bcd)\1', word):
        return True

    # 2. Check for `ஈரொற்று மயக்கம்` (three-consonant clusters)
    # Detect three consecutive pure consonants (consonant + pulli, repeated three times)
    # ([அ-ௐ]\u0bcd) matches any Tamil character followed by a pulli.
    if re.search(r'([\u0B80-\u0BFF]\u0bcd){3}', word):
        return True

    # 3. `வேற்றுநிலை மெய்ம்மயக்கம்` (different consonant clusters) - Problematic initial clusters
    problematic_initial_patterns = [
        r'ஸ்ர', r'ஸ்ம', r'ப்ர', r'க்ர', r'ச்ர', r'த்ர', r'க்ள', r'ப்ள', r'க்வ', r'ஸ்வ', r'ஹ்ர', r'க்ஷ',
        r'க்ர', r'ப்ர', r'த்ர', r'ச்ர', r'ற்ர', r'ஹ்ர', # Redundant, but ensures all from prompt are present
        r'க்ல', r'ப்ல', r'த்ல',
        r'க்வ', r'ப்வ', r'த்வ',
        r'ச்வ', r'ச்ர',
        r'ஃ[பவ]', # ஃப, ஃபௌ, ஃபா etc. (assuming ஃ is followed by a non-native sound character)
    ]

    for pattern in problematic_initial_patterns:
        if re.match(pattern, word):
            return True

    # 4. `வேற்றுநிலை மெய்ம்மயக்கம்` (different consonant clusters) - Specific internal invalid clusters
    invalid_internal_patterns = [
        r'க்த', # க்த
        r'ச்ட', # ச்ட (if 'ஷ' is replaced by 'ச')
        r'ஸ்த', # ஸ்த
        r'ஷ்ட', # ஷ்ட (using actual Grantha character)
        r'க்ஷ', # க்ஷ (conjunct)
        r'[ஸ்ஷ்ஹ்]்', # மெய்யெழுத்துக்களாக வரும்போது (e.g. ஸ், ஷ், ஹ் followed by another consonant implicitly violating rule)
        r'ஸ்ப', r'ஸ்க', r'ஸ்ட', r'ஸ்த்த', r'ஹ்ம', r'ஹ்ந', r'ஹ்ல', r'ஹ்வ' # New additions
    ]

    for pattern in invalid_internal_patterns:
        if re.search(pattern, word):
            return True

    # 5. Check for `மொழியிறுதி எழுத்துக்கள்` (valid word endings)
    # Check if the word ends with any character or two-character sequence in VALID_WORD_ENDINGS
    # Handle two-character endings (like குற்றியலுகரம்) first
    if len(word) >= 2 and word[-2:] in VALID_WORD_ENDINGS:
        return False # Valid ending
    if len(word) >= 1 and word[-1] in VALID_WORD_ENDINGS:
        return False # Valid ending

    # If none of the above rules are violated and the ending is not valid, it's a violation
    if len(word) > 0 and word[-1] not in VALID_WORD_ENDINGS and (len(word) < 2 or word[-2:] not in VALID_WORD_ENDINGS):
         # This ensures that if a word is not caught by initial/internal patterns,
         # but has an invalid ending, it's flagged.
         return True

    return False # No phonotactic violation found

def extract_all_pages_to_json(book_title):
    site = pywikibot.Site('ta', 'wikisource')

    pages_to_process = []

    main_page = Page(site, book_title)

    if not main_page.exists():
        print(f"பிழை: '{book_title}' என்ற பெயரில் நூல் ஏதும் காணப்படவில்லை.")
        return

    # Handle Index pages explicitly by parsing the 'Number of pages' parameter
    if book_title.startswith('அட்டவணை:'): # Heuristic for Index pages
        print(f"'{book_title}' ஒரு அட்டவணை நூல். அதன் உள்ளடக்கத்தை ஆராய்ந்து உட்பக்கங்கள் பிரித்தெடுக்கப்படுகின்றன...")
        index_page_content = main_page.text

        # Extract filename from the book_title itself (e.g., 'அட்டவணை:ஆடரங்கு.pdf' -> 'ஆடரங்கு.pdf')
        if ':' in book_title:
            file_name_from_title = book_title.split(':', 1)[1].strip() # Split only once to handle cases like 'Index:Book:Part.pdf'
        else:
            file_name_from_title = book_title.strip()

        # Extract 'Number of pages' parameter
        num_pages_match = re.search(r'Number of pages=(\d+)', index_page_content)
        if num_pages_match:
            total_pages = int(num_pages_match.group(1))
            print(f"Total pages found: {total_pages} for file: {file_name_from_title}")

            for i in range(1, total_pages + 1):
                page_title = f"Page:{file_name_from_title}/{i}"
                p = Page(site, page_title)
                if p.exists():
                    pages_to_process.append(p)
        else:
            print(f"எச்சரிக்கை: '{book_title}' பக்கத்தில் 'Number of pages' அளவுரு காணப்படவில்லை. மாற்று இணைப்புகள் தேடப்படவில்லை.")

    else:
        # If not an Index page, treat it as a single page or a root page with sub-pages
        pages_to_process.append(main_page)
        # Check for immediate sub-pages using links method if it's a regular page.
        # This part might need further refinement based on actual Wikisource structure
        for link in main_page.links():
            if link.title().startswith(book_title + "/"):
                pages_to_process.append(link)

    if not pages_to_process:
        print(f"'{book_title}' என்ற நூலுக்கு எந்தப் பக்கங்களும் கண்டறியப்படவில்லை.")
        return

    # Initialize new dictionaries for classification
    pure_tamil_words_dict = {}
    grantha_mixed_words_dict = {}

    print(f"மொத்தம் {len(pages_to_process)} பக்கங்கள் கண்டறியப்பட்டுள்ளன. செயலாக்கம் தொடங்குகிறது...")

    for p in pages_to_process:
        print(f"வாசிக்கப்படுகிறது: {p.title()}")
        content = p.text

        # விக்கி குறியீடுகளை (Wiki syntax) ஓரளவிற்கு நீக்குதல்
        clean_text = re.sub(r'\{\{.*?\}\}', '', content, flags=re.DOTALL) # Templates நீக்க
        clean_text = re.sub(r'\[\[|\]\]', '', clean_text) # Links நீக்க

        # வாக்கியங்களாகப் பிரித்தல்
        sentences = re.split(r'[.!?\n]', clean_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 3: # மிகச் சிறிய வரிகளைத் தவிர்க்க
                continue

            # சொற்களைப் பிரித்தல் (தமிழ் எழுத்துக்களை மட்டும் எடுக்க)
            words = re.findall(r'[\u0b80-\u0bff]+', sentence)

            for word in words:
                word_lower = word.lower() # சீரான தன்மைக்கு
                cleaned_word = clean_tamil_word(word_lower) # Apply cleaning for numbers and punarcci

                if not cleaned_word: # Skip if cleaning resulted in an empty string (e.g., if a word was just numbers)
                    continue

                # First, check if the cleaned word is a known single-letter pure Tamil word
                if cleaned_word in ORAEZHUTHU_ORUMOZI:
                    # Classify directly as pure Tamil, bypassing other checks
                    if cleaned_word not in pure_tamil_words_dict:
                        pure_tamil_words_dict[cleaned_word] = {
                            'sentences': [sentence],
                            'is_valid_initial_char': True # Single-letter words are inherently valid in this context
                        }
                    else:
                        if sentence not in pure_tamil_words_dict[cleaned_word]['sentences']:
                            pure_tamil_words_dict[cleaned_word]['sentences'].append(sentence)
                    continue # Move to the next word

                has_grantha = False
                for char in GRANTHA_CHARS:
                    if char in word: # Use original word for Grantha check as cleaning might remove characters
                        has_grantha = True
                        break

                # Check for phonotactic violations AFTER cleaning
                has_phonotactic_violation = check_tamil_phonotactics(cleaned_word)

                if has_grantha or has_phonotactic_violation:
                    # Add to grantha_mixed_words_dict
                    if cleaned_word not in grantha_mixed_words_dict:
                        grantha_mixed_words_dict[cleaned_word] = [sentence]
                    else:
                        if sentence not in grantha_mixed_words_dict[cleaned_word]:
                            grantha_mixed_words_dict[cleaned_word].append(sentence)
                else:
                    # Add to pure_tamil_words_dict with validation flag
                    is_valid_initial_char = False
                    if cleaned_word:
                        # Get the first character(s) that might be a valid initial Tamil character
                        first_char = ''
                        if len(cleaned_word) >= 1:
                            first_char = cleaned_word[0]

                        # Check if the first two chars form a valid uyirmey (e.g., 'ஞெ'), or just the first char
                        # Prioritize 2-char check if it's a valid initial char
                        if len(cleaned_word) >= 2 and cleaned_word[0:2] in VALID_INITIAL_TAMIL_CHARS:
                            first_char = cleaned_word[0:2]
                        elif len(cleaned_word) >= 1 and cleaned_word[0] in VALID_INITIAL_TAMIL_CHARS:
                            first_char = cleaned_word[0]

                        if first_char and first_char in VALID_INITIAL_TAMIL_CHARS:
                            is_valid_initial_char = True

                    if cleaned_word not in pure_tamil_words_dict:
                        pure_tamil_words_dict[cleaned_word] = {
                            'sentences': [sentence],
                            'is_valid_initial_char': is_valid_initial_char
                        }
                    else:
                        if sentence not in pure_tamil_words_dict[cleaned_word]['sentences']:
                            pure_tamil_words_dict[cleaned_word]['sentences'].append(sentence)
                        # The flag 'is_valid_initial_char' is determined once per word, so no update needed if already present

    # JSON கோப்புகளாகச் சேமித்தல்
    safe_name = book_title.replace('/', '_').replace(' ', '_').replace(':', '_') # Replace colon for filename safety

    pure_tamil_file_name = f"{safe_name}_pure_tamil.json"
    with open(pure_tamil_file_name, 'w', encoding='utf-8') as f:
        json.dump(pure_tamil_words_dict, f, ensure_ascii=False, indent=4)

    grantha_mixed_file_name = f"{safe_name}_grantha_mixed.json"
    with open(grantha_mixed_file_name, 'w', encoding='utf-8') as f:
        json.dump(grantha_mixed_words_dict, f, ensure_ascii=False, indent=4)

    print(f"\nமுழுமையாக முடிந்தது!")
    print(f"'தூய தமிழ்' சொற்கள் '{pure_tamil_file_name}' கோப்பில் சேமிக்கப்பட்டன. மொத்த தனித்துவமான சொற்கள்: {len(pure_tamil_words_dict)}")
    print(f"'கிரந்தம் கலந்த' சொற்கள் '{grantha_mixed_file_name}' கோப்பில் சேமிக்கப்பட்டன. மொத்த தனித்துவமான சொற்கள்: {len(grantha_mixed_words_dict)}")

# இயக்கம்
if __name__ == "__main__":
    book_name = input("விக்கிமூல நூலின் முதன்மைத் தலைப்பை உள்ளிடவும் (எ.க: திருக்குறள் அல்லது அட்டவணை:சிலப்பதிகாரம்.pdf): ")
    extract_all_pages_to_json(book_name)
