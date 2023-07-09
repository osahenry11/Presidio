import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.stem import PorterStemmer
from googlesearch import search
from flask import Flask, render_template, request

app = Flask(__name__)

def search_topic(topic):
    # Perform a Google search to retrieve relevant URLs
    urls = list(search(topic, num_results=5, lang='en', stop=5))

    for url in urls:
        try:
            # Send a GET request to the URL and retrieve the web content
            response = requests.get(url)
            response.raise_for_status()

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the main text content from the HTML page
            paragraphs = soup.find_all('p')
            content = ' '.join([p.text for p in paragraphs])

            # Tokenize the content into sentences
            sentences = sent_tokenize(content)

            # Process the sentences to find the most relevant answer
            answer = process_sentences(sentences, topic)
            if answer:
                return answer

        except requests.exceptions.RequestException:
            continue

    # No relevant answer found
    return "I'm sorry, I couldn't find any information on that topic."

def process_sentences(sentences, topic):
    ps = PorterStemmer()
    stemmed_topic = ps.stem(topic.lower())

    for sentence in sentences:
        tokens = sentence.lower().split()
        stemmed_tokens = [ps.stem(token) for token in tokens]

        if stemmed_topic in stemmed_tokens:
            return sentence

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form['topic']
        result = search_topic(topic)
        return render_template('index.html', result=result)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
