# Tests how much Timothy copies his own book at each Markov order.
# For orders 1 to 5 it writes new "books" with the generator and checks
# how many 10-token runs in them appear word for word in the real book.

import re
from pathlib import Path
import matplotlib.pyplot as plt

# Borrow the cleaned book and the generator from dexter_markov.py
from dexter_markov import tokens, build_chain, generate, WORD

ORDERS = [1, 2, 3, 4, 5]

# Run length: at order n, every run of n + 1 tokens is in the book by
# construction, so a fair test for order 5 needs at least 5 + 2 = 7.
# 10 is used to be safely past that and to count only clear copying.
RUN = 10

# Each sample is a new book the same length as Dexter's (8,382 words).
WORDS = sum(1 for token in tokens if re.fullmatch(WORD, token))

# Number of new books written per order. The books are random, so the
# averages are estimates and change slightly each time the script runs.
SAMPLES = 10


# 1. COLLECT EVERY 10-TOKEN RUN IN THE BOOK
book_runs = {tuple(tokens[i:i + RUN]) for i in range(len(tokens) - RUN + 1)}


# 2. MEASURE ONE SAMPLE
# Split the sample back into tokens, then count its runs that are in the book.
def copied_percent(text):
    sample = re.findall(WORD + r"|[.,!?;:]", text)
    runs = [tuple(sample[i:i + RUN]) for i in range(len(sample) - RUN + 1)]
    return 100 * sum(run in book_runs for run in runs) / len(runs)


# 3. TEST EACH ORDER
# Average the copied percentage over all the new books.
# Also count the contexts in the chain that have only one possible next word:
# the more of those, the less choice the chain has except to copy the book.
averages = []
one_choices = []

print("Order  Drinks  Copied from book (estimate)  Contexts with only one next word")
for order in ORDERS:
    chain = build_chain(order)
    results = [copied_percent(generate(chain, order, WORDS)) for _ in range(SAMPLES)]

    average = sum(results) / SAMPLES
    averages.append(average)

    one_choice = 100 * sum(1 for options in chain.values() if len(options) == 1) / len(chain)
    one_choices.append(one_choice)

    drinks = "5+" if order == 1 else str(6 - order)
    print(f"{order:5}  {drinks:>6}  {average:26.1f}%  {one_choice:31.1f}%")


output_folder = Path(__file__).parent / "outputs"
output_folder.mkdir(exist_ok=True)


# 4. CHART 1: HOW MUCH EACH ORDER COPIES
plt.figure()
plt.bar(ORDERS, averages)
plt.xlabel("Markov order (higher = fewer drinks)")
plt.ylabel(f"% of {RUN}-word runs copied from the book")
plt.title("How much does Timothy copy himself?")
plt.ylim(0, 100)
plt.savefig(output_folder / "copying_by_order.png")


# 5. CHART 2: HOW MUCH CHOICE THE CHAIN HAS
plt.figure()
plt.bar(ORDERS, one_choices)
plt.xlabel("Markov order (higher = fewer drinks)")
plt.ylabel("% of contexts with only one next word")
plt.title("How often does Timothy have only one choice?")
plt.ylim(0, 100)
plt.savefig(output_folder / "one_choice_by_order.png")

print(f"\nCharts saved to {output_folder}")
