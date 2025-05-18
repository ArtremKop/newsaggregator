import requests
from flask import Flask, render_template_string, request

API_KEY = "f1a692c276574e0caffe4fe8af450ee0"
BASE_URL = "https://newsapi.org/v2/top-headlines"

app = Flask(__name__)

SOURCES = [
    ('bbc-news', 'BBC News'),
    ('cnn', 'CNN'),
    ('al-jazeera-english', 'Al Jazeera English'),
    ('google-news', 'Google News (RSS)')
]

CATEGORIES = [
    ('', 'All Categories'),
    ('business', 'Business'),
    ('entertainment', 'Entertainment'),
    ('health', 'Health'),
    ('science', 'Science'),
    ('sports', 'Sports'),
    ('technology', 'Technology'),
]

def fetch_articles(sources=None, query=None, category=None, country='us', page_size=20):
    params = {
        'apiKey': API_KEY,
        'pageSize': page_size,
        'q': query or None,
    }

    if sources:
        params['sources'] = ','.join(sources)
    else:
        if category:
            params['category'] = category
        if country:
            params['country'] = country

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get('articles', [])


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>News Aggregator</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
<div class="container py-4">
    <h1 class="mb-4">News Aggregator</h1>
    <form method="get" class="mb-4">
        <div class="form-row">
            <div class="col-md-3 mb-2">
                <input type="text" class="form-control" name="topic" placeholder="Enter topic (optional)" value="{{ topic }}">
            </div>
            <div class="col-md-3 mb-2">
                <select class="form-control" name="category">
                    {% for cat_val, cat_label in categories %}
                        <option value="{{ cat_val }}" {% if cat_val == selected_category %}selected{% endif %}>
                            {{ cat_label }}
                        </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4 mb-2">
                <div class="form-check form-check-inline">
                    {% for src, label in sources_list %}
                        <input class="form-check-input" type="checkbox" name="source" id="src_{{ loop.index }}" value="{{ src }}"
                               {% if src in selected_sources %}checked{% endif %}>
                        <label class="form-check-label mr-3" for="src_{{ loop.index }}">{{ label }}</label>
                    {% endfor %}
                </div>
            </div>
            <div class="col-md-2 mb-2">
                <button type="submit" class="btn btn-primary btn-block">Search</button>
            </div>
        </div>
    </form>

    {% if articles %}
        <div class="row">
            {% for article in articles %}
                <div class="col-md-6 mb-4">
                    <div class="card h-100 shadow-sm">
                        {% if article.urlToImage %}
                            <img src="{{ article.urlToImage }}" class="card-img-top" alt="...">
                        {% endif %}
                        <div class="card-body">
                            <h5 class="card-title"><a href="{{ article.url }}" target="_blank">{{ article.title }}</a></h5>
                            <p class="card-text">{{ article.description or '' }}</p>
                        </div>
                        <div class="card-footer text-muted small">
                            {{ article.source.name }} | {{ article.publishedAt[:10] }}
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <p>No articles found.</p>
    {% endif %}
</div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    topic = request.args.get('topic', '')
    selected_category = request.args.get('category', '')
    selected_sources = request.args.getlist('source') or [s[0] for s in SOURCES]

    articles = fetch_articles(
        sources=selected_sources,
        query=topic or None,
        category=selected_category or None
    )

    return render_template_string(
        TEMPLATE,
        articles=articles,
        topic=topic,
        selected_category=selected_category,
        categories=CATEGORIES,
        sources_list=SOURCES,
        selected_sources=selected_sources
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

