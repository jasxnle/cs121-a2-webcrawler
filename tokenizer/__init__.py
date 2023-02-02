import re
# List<Token> tokenize(TextFile)

# This functions runs in O(nm) due to check each line in the file at a time
# and then iterating through m words in the list
def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", text)
    #exception handling


# Map<token,count> computeWordFrequencies(List<Token>)
# This function is O(n) because we are iterating through the array tokens which has a length of n.
def computeWordFrequencies(tokens):
    freq = {}

    #adding to hashmap
    for i in tokens:
        i = i.lower()
        if i not in freq:
            freq[i] = 1
        else:
            freq[i] +=1
    return freq

# This function should have a time complexity of O(nm + min(s, p)) since to tokenize each file it takes O(nm) time.
# Then finding the intersection of the two tokens for each file will take O(min(s,p)) due to having to iterate through at most all elements in the smaller array
def findCommonTokens(text1, text2):
    #tokens from each file
    tok1 = tokenize(text1)
    tok2 = tokenize(text2)

    #array that finds the common tokens using sets
    commonTok = set(tok1).intersection(set(tok2))

    #return commonTok
    return commonTok
