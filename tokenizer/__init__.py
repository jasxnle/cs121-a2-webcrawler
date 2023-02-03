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

def mergeDictionary(d1, d2):
    d3 = {**d1, **d2}
    for key, value in d3.items():
        if key in d1 and key in d2:
            d3[key] = value + d1[key]
    return d3

def generateHashes(tokens):
    res = {}
    for token in tokens:
        #res[token] = bin(int.from_bytes(hashlib.sha256(token.encode()).digest(), "little"))[-length:]
        res[token] = hash(token)
    return res

def getFinalHash(freqs, hashes):
    final_hash = [0]*64
    for i in range(64):
        for word, hash in hashes.items():
            
            if ((hash >> i) & 1) == 1:
                final_hash[i] += freqs[word]
            else:
                final_hash[i] -= freqs[word]
    
    
    for j in range(64):
        if final_hash[j] > 0:
            final_hash[j] = '1'
        else:
            final_hash[j] = '0'
    
    hash_str = ''.join(final_hash)
    print(hash_str)
    return int(hash_str, 2)

def checkSimilarity(hash1, hash2):
    numBits = 64
    numMatches = 0
    for num in range(64):
        if ((((hash1 >> num) ^ (hash2 >> num))) == 0):
            numMatches += 1

    print(numMatches/numBits)
    if numMatches/numBits > 0.9:
        return True
    return False
