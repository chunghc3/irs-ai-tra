# Implementation of RAKE - Rapid Automtic Keyword Exraction algorithm
# as described in:
# Rose, S., D. Engel, N. Cramer, and W. Cowley (2010). 
# Automatic keyword extraction from indi-vidual documents. 
# In M. W. Berry and J. Kogan (Eds.), Text Mining: Applications and Theory.unknown: John Wiley and Sons, Ltd.
# https://github.com/aneesha/RAKE/blob/master/rake.py

import re
import operator
import networkx as nx
from networkx import betweenness_centrality

debug = False
test = True


def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words
    @param stop_word_file Path and file name of a file containing stop words.
    @return list A list of stop words.
    """
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


def separate_words(text, min_word_return_size):
    """
    Utility function to return a list of all words that are have a length greater than a specified number of characters.
    @param text The text that must be split in to words.
    @param min_word_return_size The minimum no of characters a word must have to be included.
    """
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words


def split_sentences(text):
    """
    Utility function to return a list of sentences.
    @param text The text that must be split in to sentences.
    """
    sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
    sentences = sentence_delimiters.split(text)
    return sentences


def build_stop_word_regex(stop_word_file_path):
    stop_word_list = load_stop_words(stop_word_file_path)
    stop_word_regex_list = []
    for word in stop_word_list:
        word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
        stop_word_regex_list.append(word_regex)
    stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
    return stop_word_pattern


def generate_candidate_keywords(sentence_list, stopword_pattern):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "":
                phrase_list.append(phrase)
    return phrase_list


def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        #if word_list_degree > 3: word_list_degree = 3 #exp.
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  #orig.
            #word_degree[word] += 1/(word_list_length*1.0) #exp.
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    # Calculate Word scores = deg(w)/frew(w)
    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  #orig.
    #word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
    return word_score


def calculate_word_graph(phraseList):
    G = nx.Graph()
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        # build graph
        for word in word_list:
            for nei in word_list:
                if word != nei:
                    if G.has_edge(word, nei):
                        G[word][nei]["weight"] += 1
                    elif G.has_edge(nei, word):
                        G[nei][word]["weight"] += 1
                    else:
                        G.add_edge(word, nei, weight=1)
    return G


def reverse_graph_edge_weight_for_shortest_path(G):
    max_edge_weight = -1
    for edge in G.edges:
        max_edge_weight = max(max_edge_weight, G.edges[edge]["weight"])

    for edge in G.edges:
        G.edges[edge]["weight"] = max_edge_weight - G.edges[edge]["weight"]

    return G


def calculate_betweenness(G):
    return betweenness_centrality(G, None, False, "weight", True, None)


def generate_candidate_keyword_scores(phrase_list, word_score):
    keyword_candidates = {}
    for phrase in phrase_list:
        keyword_candidates.setdefault(phrase, 0)
        word_list = separate_words(phrase, 0)
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates


class Betweenness(object):
    def __init__(self, stop_words_path):
        self.stop_words_path = stop_words_path
        self.__stop_words_pattern = build_stop_word_regex(stop_words_path)

    def run(self, text):
        sentence_list = split_sentences(text)

        phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern)

        word_scores = calculate_word_scores(phrase_list)

        graph = calculate_word_graph(phrase_list)
        graph_reversed_weight = reverse_graph_edge_weight_for_shortest_path(graph)

        betweenness = calculate_betweenness(graph_reversed_weight)


        # keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)
        #
        # sorted_keywords = sorted(keyword_candidates.iteritems(), key=operator.itemgetter(1), reverse=True)
        # return sorted_keywords

        return betweenness

    def runCommon(self, text_common, text_local, text_new):
        sentence_list = split_sentences(text_common)

        phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern)

        word_scores = calculate_word_scores(phrase_list)

        graph = calculate_word_graph(phrase_list)
        graph_reversed_weight = reverse_graph_edge_weight_for_shortest_path(graph)

        betweenness = calculate_betweenness(graph_reversed_weight)

        graph_local = calculate_word_graph(
            generate_candidate_keywords(split_sentences(text_local), self.__stop_words_pattern))
        graph_new = calculate_word_graph(
            generate_candidate_keywords(split_sentences(text_new), self.__stop_words_pattern))

        filtered_betweenness_sk = {}
        for node in betweenness:
            if node in graph_local.nodes and node in graph_new.nodes:
                filtered_betweenness_sk[node] = betweenness[node]

        sorted_keywords = sorted(filtered_betweenness_sk.items(), key=operator.itemgetter(1), reverse=True)

        # keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)
        #
        # sorted_keywords = sorted(keyword_candidates.iteritems(), key=operator.itemgetter(1), reverse=True)
        # return sorted_keywords

        return sorted_keywords



# if test:
#     text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types of systems and systems of mixed types."
#
#     # Split text into sentences
#     sentenceList = split_sentences(text)
#     #stoppath = "FoxStoplist.txt" #Fox stoplist contains "numbers", so it will not find "natural numbers" like in Table 1.1
#     stoppath = "SmartStoplist.txt"  #SMART stoplist misses some of the lower-scoring keywords in Figure 1.5, which means that the top 1/3 cuts off one of the 4.0 score words in Table 1.1
#     stopwordpattern = build_stop_word_regex(stoppath)
#
#     # generate candidate keywords
#     phraseList = generate_candidate_keywords(sentenceList, stopwordpattern)
#
#     # calculate individual word scores
#     wordscores = calculate_word_scores(phraseList)
#
#     # generate candidate keyword scores
#     keywordcandidates = generate_candidate_keyword_scores(phraseList, wordscores)
#     if debug: print keywordcandidates
#
#     sortedKeywords = sorted(keywordcandidates.iteritems(), key=operator.itemgetter(1), reverse=True)
#     if debug: print sortedKeywords
#
#     totalKeywords = len(sortedKeywords)
#     if debug: print totalKeywords
#     print sortedKeywords[0:(totalKeywords / 3)]
#
#     rake = Rake("SmartStoplist.txt")
#     keywords = rake.run(text)
#     print keywords
