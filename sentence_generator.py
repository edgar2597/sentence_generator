# importing all necessary libraries
import stanfordnlp
import spacy
from spacy_stanfordnlp import StanfordNLPLanguage
import pymorphy2
from nltk import Tree
import re
import itertools
from itertools import permutations, product
import collections
from collections import Counter
import numpy as np

# training a model
snlp = stanfordnlp.Pipeline(lang="ru")
nlp = StanfordNLPLanguage(snlp)

negs_and_preps = ['не', 'ни', 'на', 'без', 'до', 'к', 'о', 'от', 'за', 'над', 'об', 'под', 'про', 'и', 'в', 'у', 'но',
                  'с', 'по', 'из', 'перед', 'для', 'при', 'что', 'через', 'после', 'вдоль', 'возле', 'около', 'вокруг',
                  'впереди', 'после']
preps = ['на', 'без', 'до', 'к', 'о', 'от', 'за', 'над', 'об', 'под', 'про', 'и', 'в', 'у', 'но', 'с', 'по', 'из',
         'перед', 'для', 'при', 'что', 'через', 'после', 'вдоль', 'возле', 'около', 'вокруг', 'впереди', 'после']
negs = ['не', 'ни']


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_

    # получение списка с подсписками


def group(d):
    a = next(d, ')')
    if a != ')':
        yield list(group(d)) if a == '(' else a
        yield from group(d)


# для варината с индексами вместо слов
def get_index(lst, c=1):
    result = []
    for i in lst:
        if isinstance(i, list):
            r, c = get_index(i, c)
            result.append(r)
        else:
            result.append(c)
            c += 1
    return result, c
    # изменения порядка фраз(перемешивание всех поддеревьев между собой внутри каждой ветви)


def swap(x):
    if isinstance(x, list):
        res = np.random.choice(x, len(x), replace=False)
        return [list(map(swap, res))]
    else:
        return x


# приводим список с подсписками в 1D список
def traverse(o, tree_types=(list, tuple)):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value, tree_types):
                yield subvalue
    else:
        yield o


# сохраняет предлог перед одним из двух последующих после него слов в оригинале

def limitation(nested):
    for index, subelement in enumerate(nested):
        if isinstance(subelement, list):
            if not limitation(subelement):
                return False
        else:
            if subelement in preps and index != 0:
                return False
    return True


# сохраняет отрицания всегда перед словами, как в оригинале
def next_of_negs(sentence):
    list_of_words = sentence.split()
    next_word = []
    for idx, word in enumerate(list_of_words):
        if word in negs:
            next_word.append(word + list_of_words[idx + 1])
    return next_word


compare = lambda x, y: collections.Counter(x) == collections.Counter(y)


# In[28]:


def sent_swapper(sentence):  # sentence без точки
    sentence = sentence.lower()
    doc = nlp(sentence)
    # дерево зависимостей и дерево составляющих
    for sent in doc.sents:
        a = to_nltk_tree(sent.root)
    nested = next(group(iter(re.findall(r'[\w\.]+|[()]', str(a)))))

    # множество вариантов предложения с перестановленными фразами в виде 1D списков
    swapped_list = []
    for i in range(10000):
        swapped_list.append(swap(nested)[0])

    swapped_list1 = []
    for element in swapped_list:
        if limitation(element):
            swapped_list1.append(list(traverse(element)))

    ss = []
    for i in [list(y) for y in set([tuple(x) for x in swapped_list1])]:
        ss.append(' '.join(word for word in i))
    s11 = [s for s in ss if s.replace('.', '').split()[-1] not in negs_and_preps]

    s44 = []
    for i in s11:
        if compare(next_of_negs(i.replace('.', '')), next_of_negs(sentence.replace('.', ''))):
            s44.append(i)
    return s44


# In[ ]:


# если предложение сложносоставное, то делать перестанвоки для каждой составной чатси и объеденять их
def sent_swapper1(sentence):
    sentence = re.sub(r" ?\([^)]+\)", "", sentence)
    if ',' in sentence:
        rezz = [(x.strip()).replace('.', '') for x in sentence.split(',')]
        newsente = [(i + '.') for i in rezz]
        newsente1 = [(sent_swapper(i)) for i in newsente]
        newsente2 = [(', '.join(i)) for i in product(*newsente1)]
        return newsente2
    else:
        return swapper(sentence)


# In[ ]:


# для сообщений
def generatorr(text):
    text.replace('«', '')
    text.replace('»', '')
    text = re.sub(r" ?\([^)]+\)", "", text)
    sentence_new = []
    for i in text.split('. '):
        sentence_new.append(i)
    swapped = []
    for i in sentence_new:
        swapped.append(sent_swapper1(i))
    res = list(zip(*map(lambda x, m=max(swapped, key=len): itertools.cycle(x) if x != m else x, swapped)))

    res1 = []
    for i in res:
        res1.append('. '.join(i))
    res1 = [i + '.' for i in res1]
    return res1

sent_swapper('Чтобы получить неограниченный доступ к новинкам модных коллекций, советам стилистов и специальным предложениям только для подписчиков, пожалуйста, подтвердите email')

