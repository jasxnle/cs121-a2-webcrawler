import re
import hashlib
from bs4 import BeautifulSoup       # FIXME: extract all soup references to worker.py
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

# tokens: takes result from computeWordFrequencies
def generateHashes(tokens):
    res = {}
    for token in tokens:
        hex_to_int = int(hashlib.md5(token.encode()).hexdigest(), 16)
        res[token] = (bin(hex_to_int)[2:]).zfill(128)
    return res

# freqs: result from computeWordFrequencies
# hashes: result from generateHashes
def getFinalHash(freqs, hashes):
    length = 128
    final_hash = [0]*length
    for i in range(length):
        for word, hash in hashes.items():
            
            if hash[i] == '1':
                final_hash[i] += freqs[word]
            else:
                final_hash[i] -= freqs[word]
    
    res = ['']*length
    for j in range(length):
        if final_hash[j] > 0:
            res[j] = '1'
        else:
            res[j] = '0'
    
    hash_str = ''.join(res)
    return hash_str

def compareHash(hash1, hash2):
    SIMILARITY_THRESHOLD = 0.6
    length = 128
    numMatches = 0
    for num in range(length):
        if (hash1[num] == hash2[num]):
            numMatches += 1

    if numMatches/length > SIMILARITY_THRESHOLD:
        return True
    return False

def checkSimilarity(resp):
    HASH_FILE_NAME = "HASH_FILE.txt"         # FIXME: choose different name per worker to make thread-safe
    # FIXME: what to return when resp is empty
    if resp is not None and resp.raw_response is not None and resp.raw_response.content is not None:
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        tokens = tokenize(soup.get_text())
        freqs = computeWordFrequencies(tokens)
        hashes = generateHashes(freqs)
        final_hash = getFinalHash(freqs, hashes)

        with open(HASH_FILE_NAME, "w+", buffering=1) as f:
            for line in f.readlines():
                # if line is not None and hashes similar, return True
                if line is not None and compareHash(final_hash, line.strip()):
                    return True

            # no similar hashes found, write hash to file
            f.write(f"{final_hash}\n")
            return False
