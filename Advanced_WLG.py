import itertools
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from tqdm import tqdm
import os

# Constants
MAX_THREADS = 10
JOIN_SYMBOLS = ["", "_", "@", "-", ".", "$", "#", "!", "&"]

# Leetspeak substitutions
LEET_DICT = {
    'a': ['a', '@', '4'],
    'b': ['b', '8'],
    'e': ['e', '3'],
    'g': ['g', '9'],
    'i': ['i', '1', '!'],
    'l': ['l', '1'],
    'o': ['o', '0'],
    's': ['s', '$', '5'],
    't': ['t', '7'],
    'z': ['z', '2']
}

def leetspeak_variations(word):
    if not word:
        return ['']
    first_char = word[0].lower()
    rest = word[1:]
    variations = leetspeak_variations(rest)
    if first_char in LEET_DICT:
        return [char + var for char in LEET_DICT[first_char] for var in variations]
    else:
        return [first_char + var for var in variations]

def process_combo(combo, years):
    mangled_words = set()
    base_word = ''.join(combo)

    # Avoid heavy leetspeak on long strings
    if len(base_word) > 12:
        leet_variants = [base_word]
    else:
        leet_variants = leetspeak_variations(base_word)

    for variant in leet_variants:
        mangled_words.add(variant)
        for year in years:
            mangled_words.add(variant + year)
            mangled_words.add(year + variant)
        for symbol in JOIN_SYMBOLS:
            joined = symbol.join(combo)
            mangled_words.add(joined)
            for year in years:
                mangled_words.add(joined + year)
                mangled_words.add(year + joined)

    return mangled_words

def generate_wordlist(words, years):
    combos = list(itertools.chain.from_iterable(
        itertools.combinations(words, r) for r in range(1, min(6, len(words)+1))
    ))
    final_words = set()
    estimated_total = len(combos)
    start_time = time.time()

    progress_lock = threading.Lock()
    processed = [0]

    def wrapped_process(combo):
        result = process_combo(combo, years)
        with progress_lock:
            processed[0] += 1
        return result

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        with tqdm(
            total=estimated_total,
            desc="\U0001F6A7 Generating",
            unit="combo",
            dynamic_ncols=True,
            ncols=100,
            bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} {unit} | ETA: {remaining} | Speed: {rate_fmt}",
        ) as pbar:
            future_to_combo = {executor.submit(wrapped_process, combo): combo for combo in combos}

            for future in future_to_combo:
                try:
                    result = future.result()
                    final_words.update(result)
                    pbar.update(1)
                except Exception as e:
                    print(f"\n[!] Error processing combo {future_to_combo[future]}: {e}")

    duration = time.time() - start_time
    real_finish = datetime.now().strftime("%I:%M:%S %p")

    print("\n\n✅ Wordlist Generation Complete!")
    print("═" * 60)
    print(f"🕓 Finished At        : {real_finish}")
    print(f"⏱  Time Taken        : {duration:.2f} seconds")
    print(f"🔢 Total Words        : {len(final_words)}")
    print("═" * 60)

    return list(final_words)

def save_wordlist(wordlist):
    filename = input("💾 Enter filename to save as (e.g., wordlist.txt): ").strip()
    if not filename:
        filename = "wordlist.txt"
    with open(filename, 'w') as f:
        for word in wordlist:
            f.write(f"{word}\n")
    file_size = os.path.getsize(filename)
    print(f"📂 Wordlist saved as  : {filename}")
    print(f"📦 File Size          : {file_size / 1024:.2f} KB ({file_size} bytes)")
    print("═" * 60)

def collect_info():
    print("\n📥 Enter the values for each category. Leave blank if not applicable.")
    categories = {
        "Names": [],
        "Nicknames / Usernames": [],
        "Company / Organization": [],
        "Location / City / Country": [],
        "Years / DOB": [],
        "Special Dates (anniversaries, etc.)": [],
        "Phone Numbers": [],
        "Pet Names / Hobbies / Interests": [],
        "Custom Words (miscellaneous)": []
    }

    all_words = []

    for category in categories:
        values = input(f"{category}: ").strip()
        if values:
            words = values.split()
            categories[category] = words
            all_words.extend(words)

    return all_words, categories.get("Years / DOB", [])

def main():
    print("\n" + "═" * 60)
    print("🔐  ADVANCED WORDLIST GENERATOR  |  Powered by Python + Threads".center(60))
    print("═" * 60)

    words, years = collect_info()
    total_combos = sum(1 for r in range(1, min(6, len(words)+1)) for _ in itertools.combinations(words, r))
    print(f"\n📦 Total combinations to process: {total_combos}")
    print(f"🚀 Multithreaded with {MAX_THREADS} threads")

    print("\n🛠  Building wordlist...")

    wordlist = generate_wordlist(words, years)
    save_wordlist(wordlist)

if __name__ == "__main__":
    # your main logic hereabhi

    main()