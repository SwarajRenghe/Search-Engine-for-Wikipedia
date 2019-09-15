# KINDS
# -----
# 0 - docID
# 1 - title
# 2 - infobox
# 3 - references
# 4 - category
# 5 - links
# 6 - body

class inverted_index ():
    def __init__ (self):
        self.titles = {}
        self.main_index = {}

    def initial_make_empty_entry (self, docID, kind):
        temp = [[docID, 0, 0, 0, 0, 0, 0]]
        temp [0][kind] = 1
        return temp
    
    def make_empty_entry (self, docID, kind):
        temp = [docID, 0, 0, 0, 0, 0, 0]
        temp [kind] = 1
        return temp

    def get_word_posting_list (self, word):
        return self.main_index[word]

    def check_word_in_main_index (self, word):
        if word in self.main_index:
            return True
        return False

    def add_new_word_to_main_index (self, word, docID, kind):
        if word is None:
            return
        self.main_index[word] = self.initial_make_empty_entry (docID, kind)

    def add_word_to_main_index (self, word, docID, kind):
        if word is None:
            return
        try:
            idx = [x[0] for x in self.main_index[word]].index(docID)
            self.main_index[word][idx][kind] += 1
        except:
            self.main_index[word].append(self.make_empty_entry(docID, kind))

    def add_title (self, docID, title):
        self.titles[docID] = title

