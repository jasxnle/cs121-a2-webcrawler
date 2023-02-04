import re
import hashlib
from bs4 import BeautifulSoup       # FIXME: extract all soup references to worker.py

def tokenize(text):
    """Would be O(N*M), where N is the number of lines and M is the number of tokens within
    the line. Since there is technically a nested for loop within the program for iterating through
    the file and the list comprehension for every token, this would have to lead to a quadratic time complexity

    Assumption: tokenizer does not handle contractions

    Args:
        text: str, extracted str from HTML content i.e. no tags

    Returns:
        List<Token>: list of tokens parsed from HTML content, includes duplicates

    """

    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    stop_words = set([ 'a','about','above','after','again','against','all','am','an','and','any','are',"aren't","as","at","be","because","been","before","being","below","between","both","but","by","can't","cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during","each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his","how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there","there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"])
    return [i.lower() for i in tokens if i.lower() not in stop_words and len(i.lower()) >= 3 ]

    # TODO: exception handling

def computeWordFrequencies(tokens):
    """From a list of tokens, create a dictionary that represents their frequency

    This function is O(n) because we are iterating through the array tokens which has a length of n.

    Args:
        tokens: List<str>, value from tokenize(text)

    Returns:
        Map<token, count>: dictionary of each token provided from tokens and the
                           frequency it shows up

    """
    freq = {}

    # adding to hashmap
    for i in tokens:
        i = i.lower()
        if i not in freq:
            freq[i] = 1
        else:
            freq[i] +=1
    return freq

def findCommonTokens(text1, text2):
    """Finds common tokens between two different text strings using tokenize() function

    This function should have a time complexity of O(nm + min(s, p)) since to
    tokenize each file it takes O(nm) time. Then finding the intersection
    of the two tokens for each file will take O(min(s,p)) due to having to
    iterate through at most all elements in the smaller array

    Args:
        text1: extracted str from HTML content i.e. no tags
        text2: extracted str from HTML content i.e. no tags

    Returns:
        List<token>: list of tokens shared by both text1 and text2

    """
    # tokens from each file
    tok1 = tokenize(text1)
    tok2 = tokenize(text2)

    # array that finds the common tokens using sets
    commonTok = set(tok1).intersection(set(tok2))

    # return commonTok
    return commonTok

def mergeDictionary(d1, d2):
    """Merges two defaultdict(int)

    Meant to merge two dictionaries from result of computeWordFrequencies

    Args:
        d1: Map<token, count> from computeWordFrequencies
        d2: Map<token, count> from computeWordFrequencies

    Returns:
        defaultdict(int): Merged defaultdict(int) combining the frequencies of
                          both dictionaries

    """
    # combine both dictionaries into d3 without combining frequencies
    d3 = {**d1, **d2}

    # loop through, if common key found merge in d3
    for key, value in d3.items():
        if key in d1 and key in d2:
            d3[key] = value + d1[key]
    return d3

def generateHashes(tokens):
    """Generate unique hash for each token using SimHash algorithm with md5 algo.

    Args:
        tokens: Map<token, count> result from computeWordFrequencies

    Returns:
        Map<token, hash>: result used in getFinalHash

    """
    res = {}
    for token in tokens:
        hex_to_int = int(hashlib.md5(token.encode()).hexdigest(), 16)
        res[token] = (bin(hex_to_int)[2:]).zfill(128)
    return res

def getFinalHash(freqs, hashes):
    """Final unique hash used to compare two hashes to test similarity

    Args:
        freqs: Map<token, count>, result from computeWordFrequencies
        hashes: Map<token, hash>, result from generateHashes

    Returns:
        str: final hash_str

    """
    # TODO: document SimHash algo
    length = 128
    final_hash = [0]*length
    # loop through each "bit" of final_hash list
    for i in range(length):
        for word, hash in hashes.items():
            # if the bit at the specified position in hash is 1, add weight of token to final_hash[i]
            if hash[i] == '1':
                final_hash[i] += freqs[word]
            # else, subtract weight of token from final_hash[i]
            else:
                final_hash[i] -= freqs[word]

    # list to represent binary string
    res = ['']*length
    for j in range(length):
        # if the jth component of final_hash is positive, set jth bit of res binary string to 1
        if final_hash[j] > 0:
            res[j] = '1'
        # else, set jth bit to 0
        else:
            res[j] = '0'

    # join list into binary string
    hash_str = ''.join(res)
    return hash_str

def compareHash(hash1, hash2):
    """Compare hashes from getFinalHash, determines if similar by SIMILARITY_THRESHOLD

    Args:
        hash1: str, result from getFinalHash
        hash2: str, result from getFinalHash
    Returns:
        bool: if hashes are within SIMILARITY_THRESHOLD

    """
    SIMILARITY_THRESHOLD = 0.9

    # TODO: document SimHash algo
    length = 128
    # the number of matches between bits in the two hashes
    numMatches = 0
    for num in range(length):
        # if the bit at hash1 is equal to the bit at hash2, that is a match, add to numMatches
        if (hash1[num] == hash2[num]):
            numMatches += 1

    # if the number of matches divided by the total number of bits is
    #  greater than similarity threshold, hashes considered similar
    if numMatches/length > SIMILARITY_THRESHOLD:
        return True
    return False

def checkSimilarity(resp):
    """Determine if incoming URL's response is similar to any of the unique hashes
    stored in HASH_FILE_NAME.

    Args:
        resp: response to check if similar to other responses
    Returns:
        bool: returns True if incoming response is similar, return False and write
              new unique hash to file otherwise

    """
    HASH_FILE_NAME = "HASH_FILE.txt"         # FIXME: choose different name per worker to make thread-safe

    # FIXME: what to return when resp is empty
    if resp is not None and resp.raw_response is not None and resp.raw_response.content is not None:

        # generate necessary tokenized data to compare hashes
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        freqs = computeWordFrequencies(tokenize(soup.get_text()))
        final_hash = getFinalHash(freqs, generateHashes(freqs))

        with open(HASH_FILE_NAME, "a+", buffering=1) as f:
            # when opening file, always start back at the beginning to check for duplicates
            f.seek(0, 0)

            # loop through hashes in file
            # if incoming response hash is similar, return True
            # otherwise, write new unique hash to file
            for line in f.readlines():
                if line is not None and compareHash(final_hash, line.strip()):
                    return True

            # no similar hashes found, write hash to file
            f.write(f"{final_hash}\n")
            return False
