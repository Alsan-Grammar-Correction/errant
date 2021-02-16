# Main ERRANT ParsedToken class
class ParsedToken:

    # Input 1: A token's text
    # Input 2: A token's lemma
    # Input 3: A token's part of speech tag
    # Input 4: A token's tag, more detailed than pos
    
    def __init__(self, text, lemma, pos, tag, dep=None):
        self.text = text
        self.lemma = lemma
        self.pos = pos
        self.tag = tag
        self.dep = dep                      # This is only needed in the Engliah classifier, never care if it doesn't exist in Arabic analyzer. 
        self.lower = self.text.lower()      # This will return a text rather than the orth

    def __len__(self):
        return len(self.text)

