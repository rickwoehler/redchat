from __future__ import unicode_literals
from django.shortcuts import render,HttpResponse
import datetime
from datetime import datetime
import praw
import re
from collections import defaultdict
import operator
###from nltk.corpus import wordnet as wn
###nouns = {x.name().split('.',1)[0] for x in wn.all_synsets('n')}


# returns individual words from a string separating on non-alphanumeric
# will keep some hyphenated words e.g. doesn
def getWords(text):
    return re.compile('\w+').findall(text)

# function to call for data from reddit
def word_counts(string,op,limit):
    r = praw.Reddit(user_agent="rdiction/0.1 by /u/lastmonk", client_id="gL0ELD92l8rgFg",client_secret="j9V8Y4tXaAd6K4yX8eBowQLSrvo")
    r.login('lastmonk','hardwork91')

#handles request for diction stats on currently trending submissions in whichever thread

    if op == "submissions":
        #submissions is a generator type object with single use
        submissions = r.get_subreddit(string).get_hot(limit=limit)

        #reddit apparently stores text in unicode, range exceeded with 8-bit encoding
        plist = [unicode(x) for x in submissions]

        # .get_hot returns a list of strings that contain
        # current post score followed by :: then title text
        # code below cuts it down to the right side of ::
        plist_titles = []
        for x in plist:
            plist_titles.append(x.split(":: ",1)[1])


        plist_words = []
        for x in plist_titles:
            for y in getWords(x):
                plist_words.append(y)

        plist_words_long = []

        # cutting out short words/fragments and puttin all lowercase
        for x in plist_words:
            if len(x) > 3 and x.isalpha() == True:
                plist_words_long.append(x.lower())

        #defaultdict type adds in x if it is not found
        plist_diction = defaultdict(int)
        for x in plist_words_long:
            plist_diction[x] += 1


        plist_diction_sorted = sorted(plist_diction.items(), key=operator.itemgetter(1), reverse = True)
        return plist_diction_sorted

        #handling requests for comment diciton stats
    elif op == "comments":
        clist = r.get_subreddit(string)
        clist_comments = clist.get_comments(limit=limit)
        clist = [unicode(x) for x in clist_comments]
        clist_words = []
        for x in clist:
            for y in getWords(x):
                clist_words.append(y)
        clist_words_long = []

        for x in clist_words:
            if len(x) > 3 and x.isalpha()==True:
                clist_words_long.append(x.lower())

        clist_diction = defaultdict(int)

        for x in clist_words_long:
            clist_diction[x] += 1
        clist_diction_sorted = sorted(clist_diction.items(), key=operator.itemgetter(1),reverse=True)
        return clist_diction_sorted

    else:
        return {}







# Create your views here.
def index(request):
    return render(request,
    'timedisplay/index.html')
    #might have lazily used the time display assignment to work from

# considered adding feature for user to
#specify words they wanted to exclude, or to have
#the option to exclude parts of speech or not and base
#that off of a list or dictionary I specify. Leaving
#that out for now.

def results(request):

    limit = int(request.GET['limit'])
    sub = request.GET['source']
    op = request.GET['op']
    #ntest = request.GET['ntest']

    diction = word_counts(sub, op,limit)
    #cut_list = ["this","that","they","what","have","will","with","https","been","just","from","there","they","them","these","your","those","didn","their","were","both","many","http","about","doesn","than","which","though","most","well","then","only","where","some","does",""]

    #if ntest == "yes":
    #    dtemp = {key:value for key,value in diction.items() if key in nouns}
    context = {
    "diction":diction,
    #"exclude":exclude
    }
    return render(request,'timedisplay/results.html',context)
