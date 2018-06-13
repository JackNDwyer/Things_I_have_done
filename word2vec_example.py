# imports needed and logging
import gzip
import gensim
import logging
from bs4 import BeautifulSoup,SoupStrainer
from os import listdir
from os.path import isfile, join

onlyfiles = [join('Downloads/reuters21578', f) for f in listdir('Downloads/reuters21578') if isfile(join('Downloads/reuters21578', f))]
print onlyfiles
onlyfiles = [ x for x in onlyfiles if "sgm" in x ]
list = []
for f in onlyfiles:
    text = open(f, 'r')
    data= text.read()
    soup = BeautifulSoup(data, "html5lib")
    topics= soup.findAll('body') # find all body tags
    print len(topics)  # print number of body tags in sgm file
    i=0
    mini_list = []
    for link in topics:         #loop through each body tag and print its content
        children = link.findChildren()
        for child in children:
            if i==0:
                mini_list.append(child.text)
            else:
                print "none"
                i=i+1
    list.extend(mini_list)
model = gensim.models.Word2Vec(
        list,
        size=150,
        window=10,
        min_count=2,
        workers=10, hs=1, negative=0)
model.train(list, total_examples=len(list), epochs=2)
print model.score(["The fox jumped over a lazy dog".split()])
#model.wv.most_similar(positive = ['signed'])
