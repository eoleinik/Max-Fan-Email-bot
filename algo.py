import nltk
import json
import xmltodict
import xml
from nltk.tokenize import word_tokenize
#from nltk.corpus import stopwords
#from nltk.stem import PorterStemmer


import re
def cleanhtml(raw_html):
    cleanr=re.compile('<.*?>')
    cleantext = re.sub(cleanr,'', raw_html)
    return cleantext

def load_event_data():
    with open('content2016.json', 'rb') as f:
        event_data = json.load(f)
    event_results = {}
    for event in event_data:
        location = event['event'].split()[-1].lower()
        event_results[location] = event
    return event_results


def load_news():
    def remove_tags(text):
        return ''.join(xml.etree.ElementTree.fromstring(text).itertext())

    with open('news.xml') as f:
        doc = xmltodict.parse(f.read())
        list_articles =  doc['rss']['channel']['item']
        all_articles = []
        for art in list_articles:
            complete_text = art['title']+'\n'+cleanhtml(art['description'])
            all_words = nltk.FreqDist(complete_text)
            all_articles.append((all_words, complete_text))

    return all_articles


def clean_query(query):
    word_tokens = word_tokenize(query)
    #stop_words = set(stopwords.words('english'))
    #filtered_sentence = [w for w in word_tokens if w not in stop_words]

    #ps = PorterStemmer()
    #stemmed = [ps.stem(w) for w in filtered_sentence]
    return word_tokens
    #ne_recognition(word_tokens)


event_results = load_event_data()
place_results = {
    'spain': '1st',
    'russia': 'RET',
    'china': '8th',
    'bahrain': '6th',
    'australia': '10th'
}

#query = 'What time do you finish the race of the Formula 1 Monaco?'
#query = 'What do you think of the Formula 1 Belgium'
#query = 'Tell me about history of Russia?'
#query = 'Which place did you end in China?'
#query = 'Wanna go for a date?'

def find_country(tagged_query):
    for (word, pos) in tagged_query:
        if pos == 'NNP':
            if word.lower() in event_results.keys():
                return word.lower()
    return None

def answer_question(query):

    cleaned = clean_query(query)
    tagged = nltk.pos_tag(cleaned)
    print tagged
    country = find_country(tagged)
    lower_query = query.lower()
    if country:
        # asking for quote
        current = event_results[country]
        if any(w in lower_query for w in ['think', 'opinion', 'quote']):
            return current['track']['quote']
        # asking for description
        if any(w in lower_query for w in ['more', 'info', 'track', 'circuit', 'description', 'describe']):
            return current['track']['description']
        # asking for history
        if any(w in lower_query for w in ['history']):
            return current['track']['history']
        # asking for time
        if any(w in lower_query for w in ['time', 'when', 'day', 'date']):
            current = current['schedule']
            if any(w in lower_query for w in ['qualifying', 'qualification']):
                current = current['Qualifying']
                if any(w in lower_query for w in ['start', 'begin', 'from']):
                    return current['time_from'].split('+')[0]
                if any(w in lower_query for w in ['finish', 'end', 'to']):
                    return current['time_to'].split('+')[0]
                else:
                    return current['date']
            if all(w in lower_query for w in ['free', 'practice']):
                round = 1
                if '3' in lower_query:
                    round = 3
                elif '2' in lower_query:
                    round = 2
                current = current['Free practice '+str(round)]
                if any(w in lower_query for w in ['start', 'begin', 'from']):
                    return current['time_from'].split('+')[0]
                if any(w in lower_query for w in ['finish', 'end', 'to']):
                    return current['time_to'].split('+')[0]
                else:
                    return current['date']
            else:
                current = current['Race']
                if any(w in lower_query for w in ['start', 'begin', 'from']):
                    return current['time_from'].split('+')[0]
                if any(w in lower_query for w in ['finish', 'end', 'to']):
                    return current['time_to'].split('+')[0]
                else:
                    return current['date']
        # asking for place
        if any(w in lower_query for w in ['place', 'position']):
            if country in place_results.keys():
                return place_results[country]+' place'
            return 'N/A'
        # in case of failure, return all info about track
        return str(current) # dump all event stats (ouch)
    # Random stuff
    if any(w in lower_query for w in ['team']):
        return 'Red Bull Racing'
    if any(w in lower_query for w in ['name']):
        return 'Max Verstappen'
    if any(w in lower_query for w in ['old']):
        return '18 years old'
    if any(w in lower_query for w in ['birth', 'born']):
        return '30 September 1997 in Hasselt, Belgium'
    return "Ok, I don't understand your question '" + query + "'."

print answer_question('When does free practice 3 in Russia end?')