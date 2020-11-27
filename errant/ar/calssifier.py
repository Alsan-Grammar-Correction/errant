# Input: An Edit object
# Output: The same Edit object with an updated error type

'''
Actions: {Edit, Add, Merge, Split, Delete, Move, Other}


2-4 ==> 2-3

o_end - o_start = 2 or more
c_end - c_start = 1 or more but less than the above
o_end - o_start > c_end - c_start
Merge 


2-4 ==> 2-2

o_end - o_start = n , a positive number     # Not important
c_end - c_start = 0 
o_end - o_start > c_end - c_start           # This is not necessary as any positive numbers is grater than 0 
Delete 


o_end - o_start = 1                         # What if 2 words are splitted to three words? 
c_end - c_start = 2                         # What if 2 words are splitted to three words?    
o_end - o_start < c_end - c_start            
2-3 ==> 2-4
Split 


o_end-o_start = n > 1     
c_end-c_start = n > 1                           
o_end-o_start = c_end-c_start
sorted(orignal tokens) == sorted(correction tokens)             # The blocks of words are the same
2-3 ==> 2-3
Move


o_end-o_start = 1                           # Maybe more than one word has been edited? 
c_end-c_start = 1                           # Maybe more than one word has been edited?
o_end-o_start = c_end-c_start
2-3 ==> 2-3
Edit


o_end - o_start = 0
c_end - c_start = 1                         # How if more than one word is added?
o_end - o_start < c_end - c_start           # This is not necessary as 0 is less than any positive numbers
2-2 ==> 2-3
Add
'''

def classify(edit):
    
    orig_offset_diff = edit.o_end - edit.o_start
    cor_offset_diff = edit.c_end - edit.c_start
    
    if orig_offset_diff == 0:
        edit.type = "Add"

    elif cor_offset_diff == 0:
        edit.type = "Delete"

    # Note: The sorted function is used with strings rather than token ids to decrease dependency on spacy library
    elif orig_offset_diff == cor_offset_diff and orig_offset_diff > 1 and sorted(edit.o_str.split()) == sorted(edit.c_str.split()):  
        edit.type = "Move"

    # Edit must be after move, as it rwquires part of the conditions
    elif orig_offset_diff == cor_offset_diff:
        edit.type = "Edit"

    elif orig_offset_diff < cor_offset_diff:
        edit.type = "Split"

    elif orig_offset_diff > cor_offset_diff:
        edit.type = "Merge"

    else:
        edit.type = "Other"
    
    return edit