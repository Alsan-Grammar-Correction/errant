from itertools import combinations, groupby
from re import sub
from string import punctuation
import Levenshtein
import spacy.symbols as POS
from errant.edit import Edit

# Merger resources
open_pos = {POS.ADJ, POS.AUX, POS.ADV, POS.NOUN, POS.VERB}              # Not sure if it is language dependent. 

# Input: An Alignment object
# Output: A list of Edit objects
def get_rule_edits(alignment, lang):
    edits = []
    # Split alignment into groups of M, T and rest. (T has a number after it)
    for op, group in groupby(alignment.align_seq, 
            lambda x: x[0][0] if x[0][0] in {"M", "T"} else False):
        group = list(group)
        # Ignore M
        if op == "M": continue
        # T is always split
        elif op == "T":
            for seq in group:
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
        # Process D, I and S subsequence
        else:
            processed = process_seq(group, alignment)
            # Turn the processed sequence into edits
            for seq in processed: 
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
    return edits

# Input 1: A sequence of adjacent D, I and/or S alignments
# Input 2: An Alignment object
# Output: A sequence of merged/split alignments
def process_seq(seq, alignment):
    # Return single alignments
    if len(seq) <= 1: return seq
    # Get the ops for the whole sequence
    ops = [op[0] for op in seq]
    # Merge all D xor I ops. (95% of human multi-token edits contain S).
    if set(ops) == {"D"} or set(ops) == {"I"}: return merge_edits(seq)

    content = False # True if edit includes a content word
    # Get indices of all start-end combinations in the seq: 012 = 01, 02, 12
    combos = list(combinations(range(0, len(seq)), 2))
    # Sort them starting with largest spans first
    combos.sort(key = lambda x: x[1]-x[0], reverse=True)
    # Loop through combos
    for start, end in combos:
        # Ignore ranges that do NOT contain a substitution.
        if "S" not in ops[start:end+1]: continue
        # Get the tokens in orig and cor. They will now never be empty.
        o = alignment.orig[seq[start][1]:seq[end][2]]
        c = alignment.cor[seq[start][3]:seq[end][4]]
        # Merge possessive suffixes: [friends -> friend 's]
        if o[-1].tag == "POS" or c[-1].tag == "POS":                              # what is POS? + change tag_ to tag
            return process_seq(seq[:end-1], alignment) + \
                merge_edits(seq[end-1:end+1]) + \
                process_seq(seq[end+1:], alignment)
        # Case changes
        if o[-1].lower == c[-1].lower:                                              # This is not applied on Arabic
            # Merge first token I or D: [Cat -> The big cat]
            if start == 0 and (len(o) == 1 and c[0].text[0].isupper()) or \
                    (len(c) == 1 and o[0].text[0].isupper()):                       # This is not applied on Arabic
                return merge_edits(seq[start:end+1]) + \
                    process_seq(seq[end+1:], alignment)
            # Merge with previous punctuation: [, we -> . We], [we -> . We]
            if (len(o) > 1 and is_punct(o[-2])) or \
                    (len(c) > 1 and is_punct(c[-2])):
                return process_seq(seq[:end-1], alignment) + \
                    merge_edits(seq[end-1:end+1]) + \
                    process_seq(seq[end+1:], alignment)
        # Merge whitespace/hyphens: [acat -> a cat], [sub - way -> subway]
        s_str = sub("['-]", "", "".join([tok.lower for tok in o]))             # change lower_ to lower. This is not applied on Arabic
        t_str = sub("['-]", "", "".join([tok.lower for tok in c]))             # change lower_ to lower. This is not applied on Arabic
        if s_str == t_str:
            return process_seq(seq[:start], alignment) + \
                merge_edits(seq[start:end+1]) + \
                process_seq(seq[end+1:], alignment)
        # Merge same POS or auxiliary/infinitive/phrasal verbs:
        # [to eat -> eating], [watch -> look at]
        pos_set = set([tok.pos for tok in o]+[tok.pos for tok in c])            # This is not applied on Arabic
        if len(o) != len(c) and (len(pos_set) == 1 or \
                pos_set.issubset({POS.AUX, POS.PART, POS.VERB})):               # Not sure if it is language dependent. This is not applied on Arabic
            return process_seq(seq[:start], alignment) + \
                merge_edits(seq[start:end+1]) + \
                process_seq(seq[end+1:], alignment)
        # Split rules take effect when we get to smallest chunks
        if end-start < 2:
            # Split adjacent substitutions
            if len(o) == len(c) == 2:
                return process_seq(seq[:start+1], alignment) + \
                    process_seq(seq[start+1:], alignment)
            # Split similar substitutions at sequence boundaries
            if (ops[start] == "S" and char_cost(o[0], c[0]) > 0.75) or \
                    (ops[end] == "S" and char_cost(o[-1], c[-1]) > 0.75):
                return process_seq(seq[:start+1], alignment) + \
                    process_seq(seq[start+1:], alignment)
            # Split final determiners
            if end == len(seq)-1 and ((ops[-1] in {"D", "S"} and \
                    o[-1].pos == POS.DET) or (ops[-1] in {"I", "S"} and \
                    c[-1].pos == POS.DET)):                                     # This is not applied on Arabic
                return process_seq(seq[:-1], alignment) + [seq[-1]]
        # Set content word flag
        if not pos_set.isdisjoint(open_pos): content = True                     # Not sure if it is language dependent.
    # Merge sequences that contain content words
    if content: return merge_edits(seq)
    else: return seq

# Check whether token is punctuation
def is_punct(token):
    return token.pos == POS.PUNCT or token.text in punctuation          # needs Arabic punctuations

# Calculate the cost of character alignment; i.e. char similarity
def char_cost(a, b):
    return Levenshtein.ratio(a.text, b.text)
    
# Merge the input alignment sequence to a single edit span
def merge_edits(seq):
    if seq: return [("X", seq[0][1], seq[-1][2], seq[0][3], seq[-1][4])]
    else: return seq