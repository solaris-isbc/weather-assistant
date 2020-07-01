import re

class IrrelevanceDetector():

    global tokens

    def define_tokens(self):
        self.tokens = ["wetter","regen","regne","sonne","schein","wind","sturm","gewitter","stürm","blitz","donner","druck","luftdruck","hurrikan","wirbelsturm","grad","celsius","temperatur","kalt","warm","t-shirt","kurze hose","heiß","schnee","schnei","wolken","bewölk","wolkig","nebel","neblig","sonnig","wölkig"]


    def query_has_relevant_tokens(self, query):
        self.define_tokens()
        num_of_relevant = 0
        for token in self.tokens:
            if bool(re.search(token, query, re.IGNORECASE)):
                num_of_relevant += 1
        if num_of_relevant > 0:
            return True
        else:
            return False


irrelevance_detector = IrrelevanceDetector()