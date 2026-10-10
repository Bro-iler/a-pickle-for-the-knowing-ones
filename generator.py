import re
import random
from pathlib import Path
from collections import defaultdict, Counter

# Download from https://www.gutenberg.org/cache/epub/43453/pg43453.txt
BOOK_FILE = Path(__file__).parent / "data" / "pg43453.txt"

# Words
WORD = r"[A-Za-z]+(?:['-][A-Za-z]+)*"

# Loading the book
text = BOOK_FILE.read_text(encoding="utf-8")

# Skip preface and stop before the appendix.
start = re.search(r"A PICKLE\s+FOR THE KNOWING ONES\.", text).end()
end = text.find("APPENDIX.", start)
text = text[start:end]

# Remove notes such as page numbers [8]
text = re.sub(r"\[[^\]]*\]", " ", text)

# Remove all-capital headings and signatures
lines = [line for line in text.splitlines() if not line.strip().isupper()]
text = " ".join(lines)

# Each token is a word or a punctuation mark
tokens = re.findall(WORD + r"|[.,!?;:]", text)

# THE MARKOV CHAIN
# For every run of `order` tokens, count which token comes right after it.
def build_chain(order):
    chain = defaultdict(Counter)
    for i in range(len(tokens) - order):
        state = tuple(tokens[i:i + order])
        chain[state][tokens[i + order]] += 1
    return chain


# Generate text
def count_words(output):
    return sum(1 for token in output if re.fullmatch(WORD, token))


def generate(chain, order, word_count):
    state = random.choice(list(chain))
    output = list(state)
    words = count_words(output)

    while words < word_count:
        # The end of the book has nothing after it, so jump somewhere random.
        if state not in chain:
            state = random.choice(list(chain))

        # Pick the next token, weighted by how often it followed this state.
        options = chain[state]
        token = random.choices(list(options), weights=list(options.values()))[0]
        output.append(token)
        if re.fullmatch(WORD, token):
            words += 1

        # Slide the state along by one token
        state = state[1:] + (token,)

    # The starting state can hold more words than asked for
    while count_words(output) > word_count:
        output.pop()

    # Join with spaces then remove the space before punctuation.
    return re.sub(r" ([.,!?;:])", r"\1", " ".join(output))

def ask_number(question, minimum):
    while True:
        answer = input(question)
        if answer.isdigit() and int(answer) >= minimum:
            return int(answer)
        print(f"Please enter a whole number of at least {minimum}.")

if __name__ == "__main__":
    print("ANOTHER PICKLE FOR THE KNOWING ONES - TIMOTHY DEXTER SPEAKS\n")
  
    # 5 or more drinks = order 1, 4 = order 2, 3 = order 3, 2 = order 4,
    # 1 = order 5.
    drinks = ask_number("How many drinks has Timothy had? ", 0)
    if drinks == 0:
        print()
        print("I Lord Timothy Dexter am sober as A Judg this Day and A sober man "
              "Speaks only what he has Rote so go Reed my grate Littel book A Pickle "
              "for the knowing ones it is all trouth and Rite for the peopel and "
              "my frinds and sum fools two")
        print("\nhttps://www.gutenberg.org/ebooks/43453")
    else:
        word_count = ask_number("How many words should Timothy speak? ", 1)
        order = max(1, 6 - drinks)
        chain = build_chain(order)
        print()
        print(generate(chain, order, word_count))
