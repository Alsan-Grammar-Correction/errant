from itertools import combinations, groupby
from re import sub
from string import punctuation
import Levenshtein
import spacy.symbols as POS
from errant.edit import Edit
import errant.parsedToken 
import re
from fuzzywuzzy import fuzz
#windows path
#f = open( r'C:\Users\MSI\Documents\GitHub\errant-docs\run-errant\testing_file.txt' , "w", encoding ='utf-8')
#split_f = open( r'C:\Users\MSI\Documents\GitHub\errant-docs\run-errant\split_function.txt' , "w", encoding ='utf-8')
#mac path
f = open( r'/Users/Jumana/Desktop/git/errant-docs/run-errant/testing_file.txt' , "w", encoding ='utf-8')
split_f = open( r'/Users/Jumana/Desktop/git/errant-docs/run-errant/split_function.txt' , "w", encoding ='utf-8')
# Merger resources
#--edited--# open_pos = {POS.ADJ, POS.AUX, POS.ADV, POS.NOUN, POS.VERB} 
open_pos = {'adj','adj_comp','adj_num','adv','adv_interrog','adv_rel','noun','noun_prop','noun_num','noun_quant','verb','verb_pseudo'} #Testing a version of open_pos that works with arabic (because camel_tools' morphological analyzer produces textual tags)

#Arabic punctation regex
arab_punct_rx=r"[\".,:;!?،؛؟]"
arab_punct = re.compile(arab_punct_rx)

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
            if lang == 'ar':
                processed = process_seq_ar(group, alignment)
            else:
                processed = process_seq_en(group, alignment)
            # Turn the processed sequence into edits
            for seq in processed: 
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
    return edits

# Input 1: A sequence of adjacent D, I and/or S alignments
# Input 2: An Alignment object
# Output: A sequence of merged/split alignments
def process_seq_ar(seq, alignment):
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
 
        #hyphens removed (they were messing up some edits but might rewrite it later)
        s_str = sub("['-]", "", "".join([tok.lower for tok in o]))             # change lower_ to lower. This is not applied on Arabic
        t_str = sub("['-]", "", "".join([tok.lower for tok in c]))             # change lower_ to lower. This is not applied on Arabic
        
        s_str_spaces = sub("['-]", " ", " ".join([tok.lower for tok in o]))             # change lower_ to lower. This is not applied on Arabic
        t_str_spaces = sub("['-]", " ", " ".join([tok.lower for tok in c]))             # change lower_ to lower. This is not applied on Arabic
        
        split_f.write("char cost: "+str(char_cost(s_str , t_str))+"\n")
        split_f.write("char cost (with spaces): "+str(char_cost(s_str_spaces , t_str_spaces))+"\n")

    #---------------------START TESTING SPACE---------------------#
        correct_pos=list()
        original_pos=list()

        correct_token=list()
        original_token=list()

        #correct_ops=list()
        #original_ops=list()
    
        correct_tok_dict={}
        origonal_tok_dict={}
    
        for tok in c:
            correct_token.append(tok.text)
            correct_pos.append(str(tok.pos))
            

        for tok in o:
            original_token.append(tok.text)
            original_pos.append(str(tok.pos))
  
        correct_tok_dict=dict(zip(correct_token, correct_pos))
        origonal_tok_dict=dict(zip(original_token, original_pos))

        f.write("seq: "+str(seq) +"\n")
        f.write("original: "+str(sub("['-]", " ", " ".join([tok.lower for tok in o])) )+"\n")
        f.write("correction: "+str(sub("['-]", " ", " ".join([tok.lower for tok in c])))+"\n")
        f.write("original: "+str(origonal_tok_dict)+"\n")
        f.write("correction: "+str(correct_tok_dict)+"\n")
        f.write(str(correct_tok_dict)+"\n")
        f.write(str(set(ops))+"\n")
        f.write("     \n       \n")
        #split_f.write("o :"+str(o)+"\n")
        #split_f.write("c :"+str(c)+"\n")
        split_f.write("s_str_spaces  :"+s_str_spaces+"\n")

        split_f.write("t_str_spaces :"+t_str_spaces+"\n")
        lev_distance = [char_cost(tok.text , s_str_spaces) for tok in c]
        #ww = [char_cost(tok , t_str_spaces[0]) for tok in o]
        spaces_in_s=len(re.findall(r"[\s]+", s_str_spaces))
        spaces_in_t=len(re.findall(r"[\s]+", t_str_spaces))
        split_f.write("lev_distance: "+str(lev_distance)+"     \n")
        #split_f.write("t_str_spaces :"+str(spaces_in_t)+"\n")
        split_f.write("s_str_spaces :"+str(s_str_spaces.count(' '))+"\n")
        split_f.write("t_str_spaces :"+str(t_str_spaces.count(' '))+"\n")
        
        split_f.write("#####################################################\n")

#        split_f.write("alignment :"+str(alignment)+"\n")
#        split_f.write("seq :"+str(seq)+"\n")
    #---------------------END TESTING SPACE---------------------#
            ##If a punctation mark is encontered, remove it
            ##I wrote this to remove splits involving punctation marks            
        arab_punct_set=set([is_punct(tok) for tok in c])
        if True in arab_punct_set:
                return process_seq_ar(seq[:start+1], alignment) + \
                process_seq_ar(seq[start+1:], alignment) 

        if s_str == t_str:
            return process_seq_ar(seq[:start], alignment) + \
                merge_edits(seq[start:end+1]) + \
                process_seq_ar(seq[end+1:], alignment)


        if spaces_in_t > spaces_in_s and not any(i < 0.65 for i in lev_distance):
                split_f.write(s_str_spaces+"z\n")
                split_f.write(t_str_spaces+"z\n")
                return process_seq_ar(seq[:start], alignment) + \
                    merge_edits(seq[start:end+1]) + \
                    process_seq_ar(seq[end+1:], alignment)

              
        # Split rules take effect when we get to smallest chunks
        if end-start <2:

            # Split adjacent substitutions
            if len(o) == len(c) == 2:
                return process_seq_ar(seq[:start+1], alignment) + \
                    process_seq_ar(seq[start+1:], alignment)

            # Split similar substitutions at sequence boundaries
            if (ops[start] == "S" and char_cost(o[0].text, c[0].text) > 0.75) or \
                    (ops[end] == "S" and char_cost(o[-1].text, c[-1].text) > 0.75):
                return process_seq_ar(seq[:start+1], alignment) + \
                    process_seq_ar(seq[start+1:], alignment)


  

        # Set content word flag
        #if not pos_set.isdisjoint(open_pos): content = True                     # Not sure if it is language dependent.
    # Merge sequences that contain content words
    if content: return merge_edits(seq)
    else: return seq

# Input 1: A sequence of adjacent D, I and/or S alignments
# Input 2: An Alignment object
# Output: A sequence of merged/split alignments
def process_seq_en(seq, alignment):
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
            return process_seq_en(seq[:end-1], alignment) + \
                merge_edits(seq[end-1:end+1]) + \
                process_seq_en(seq[end+1:], alignment)
        # Case changes
        if o[-1].lower == c[-1].lower:                                              # This is not applied on Arabic
            # Merge first token I or D: [Cat -> The big cat]
            if start == 0 and (len(o) == 1 and c[0].text[0].isupper()) or \
                    (len(c) == 1 and o[0].text[0].isupper()):                       # This is not applied on Arabic
                return merge_edits(seq[start:end+1]) + \
                    process_seq_en(seq[end+1:], alignment)
            # Merge with previous punctuation: [, we -> . We], [we -> . We]
            if (len(o) > 1 and is_punct(o[-2])) or \
                    (len(c) > 1 and is_punct(c[-2])):
                return process_seq_en(seq[:end-1], alignment) + \
                    merge_edits(seq[end-1:end+1]) + \
                    process_seq_en(seq[end+1:], alignment)
        # Merge whitespace/hyphens: [acat -> a cat], [sub - way -> subway]
        s_str = sub("['-]", "", "".join([tok.lower for tok in o]))             # change lower_ to lower. This is not applied on Arabic
        t_str = sub("['-]", "", "".join([tok.lower for tok in c]))             # change lower_ to lower. This is not applied on Arabic
        if s_str == t_str:
            return process_seq_en(seq[:start], alignment) + \
                merge_edits(seq[start:end+1]) + \
                process_seq_en(seq[end+1:], alignment)
        # Merge same POS or auxiliary/infinitive/phrasal verbs:
        # [to eat -> eating], [watch -> look at]
        pos_set = set([tok.pos for tok in o]+[tok.pos for tok in c])            # This is not applied on Arabic
        if len(o) != len(c) and (len(pos_set) == 1 or \
                pos_set.issubset({POS.AUX, POS.PART, POS.VERB})):               # Not sure if it is language dependent. This is not applied on Arabic
            return process_seq_en(seq[:start], alignment) + \
                merge_edits(seq[start:end+1]) + \
                process_seq_en(seq[end+1:], alignment)
        # Split rules take effect when we get to smallest chunks
        if end-start < 2:
            # Split adjacent substitutions
            if len(o) == len(c) == 2:
                return process_seq_en(seq[:start+1], alignment) + \
                    process_seq_en(seq[start+1:], alignment)
            # Split similar substitutions at sequence boundaries
            if (ops[start] == "S" and char_cost(o[0].text, c[0].text) > 0.75) or \
                    (ops[end] == "S" and char_cost(o[-1].text, c[-1].text) > 0.75):
                return process_seq_en(seq[:start+1], alignment) + \
                    process_seq_en(seq[start+1:], alignment)
            # Split final determiners
            if end == len(seq)-1 and ((ops[-1] in {"D", "S"} and \
                    o[-1].pos == POS.DET) or (ops[-1] in {"I", "S"} and \
                    c[-1].pos == POS.DET)):                                     # This is not applied on Arabic
                return process_seq_en(seq[:-1], alignment) + [seq[-1]]
        # Set content word flag
        if not pos_set.isdisjoint(open_pos): content = True                     # Not sure if it is language dependent.
    # Merge sequences that contain content words
    if content: return merge_edits(seq)
    else: return seq

# Check whether token is punctuation
#First, check the token's type:
#If the token was a parsedToken, check if the POS=PUNC
#Else if the token was a string, then check if it matches the arab punct regex
def is_punct(token):
    if(isinstance(token,errant.parsedToken.ParsedToken)):
        return token.pos=="punc" or token.pos == POS.PUNCT or token.text in punctuation   # needs Arabic punctuations
    elif(isinstance(token, str)):
       return bool(arab_punct.match(token))
# Calculate the cost of character alignment; i.e. char similarity
# Input 1: string a 
# Input 2: string b 
def char_cost(a, b):
    return Levenshtein.ratio(a, b)
    
# Merge the input alignment sequence to a single edit span
def merge_edits(seq):
    if seq: return [("X", seq[0][1], seq[-1][2], seq[0][3], seq[-1][4])]
    else: return seq