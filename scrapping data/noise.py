import random
import re
import json


def add_text_noise(text, char_noise_level=0.05, punct_noise_level=0.1):
    """
    Adds only:
    1. Character-level noise (insertions, deletions, substitutions, swaps)
    2. Punctuation noise (adding/removing spaces around punctuation)
    
    Excludes:
    - Word-level modifications
    - Diacritic/harakat modifications
    """
    arabic_chars = 'ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوىي'
    punctuation = '.,،;؛!؟?'
    
    # Character-level noise
    text_chars = list(text)
    i = 0
    while i < len(text_chars):
        if random.random() < char_noise_level and text_chars[i].strip():  # Don't modify spaces
            choice = random.randint(0, 3)
            
            # Insert random Arabic character
            if choice == 0:
                text_chars.insert(i, random.choice(arabic_chars))
                i += 1
                
            # Delete character
            elif choice == 1:
                text_chars[i] = ''
                
            # Substitute character
            elif choice == 2:
                text_chars[i] = random.choice(arabic_chars)
                
            # Swap with next character
            elif choice == 3 and i < len(text_chars) - 1:
                text_chars[i], text_chars[i+1] = text_chars[i+1], text_chars[i]
                i += 1
        i += 1
    
    text = ''.join(text_chars)
    
    # Punctuation noise
    if random.random() < punct_noise_level:
        # Add/remove spaces around punctuation
        text = re.sub(r'([{}])'.format(punctuation), 
                     lambda m: ' ' + m.group(1) + ' ' if random.random() < 0.5 else m.group(1), 
                     text)
    
    if random.random() < punct_noise_level/2:
        # Randomly duplicate punctuation
        text = re.sub(r'([{}])'.format(punctuation),
                     lambda m: m.group(1)*random.randint(1, 3),
                     text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    
    return text



def add_noise_to_json(input_file, output_file, char_noise=0.05, punct_noise=0.1):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for article in data:
        if 'title' in article:
            article['title'] = add_text_noise(article['title'], char_noise, punct_noise)
        if 'text' in article:
            article['text'] = add_text_noise(article['text'], char_noise, punct_noise)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Usage
add_noise_to_json('clean_articles.json', 'noisy_articles.json', char_noise=0.07, punct_noise=0.15)