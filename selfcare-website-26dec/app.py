import pickle 
import numpy as np
from flask import Flask, render_template, request, jsonify
from interact1 import run

books = pickle.load(open('./models/books.pkl', 'rb'))
popular_df = pickle.load(open('./models/popular.pkl', 'rb'))
pivot_table = pickle.load(open('./models/pivot_table.pkl', 'rb'))
similarity_scores = pickle.load(open('./models/similarity_scores.pkl', 'rb'))


app = Flask(__name__)

@app.get("/")
def index_get():
    return render_template("base.html")
 
@app.post("/predict")
def predict():

    text = request.get_json().get("message")
    response = run(text)
    print(response)
    message = {"answer":response}

    return jsonify(message)

@app.route('/recommendation', methods=['POST'])
def recommend_books():
    user_input = request.form.get('user_input', '').strip().lower()

    indices = np.where(pivot_table.index.str.lower() == user_input)[0]
    idx = indices[0] if indices.size > 0 else None

    if idx is None:
        return render_template('base.html', error="Book not found. Please try again.")

    top_indices = np.argsort(similarity_scores[idx])[::-1][1:7]
    recommendations = []

    for i in top_indices:
        book_title = pivot_table.index[i]

        book_info = books[
            books['Book-Title'] == book_title
        ].drop_duplicates('Book-Title')

        if book_info.empty:
            continue

        title = book_info['Book-Title'].values[0]
        author = book_info['Book-Author'].values[0]
        image_url = book_info[f'Image-URL-L'].values[0]

        if image_url.startswith('http://'):
            image_url = 'https://' + image_url[7:]

        recommendations.append([title, author, image_url])

    if not recommendations:
        return render_template('base.html', error="No recommendations found. Please try again.")

    return render_template('base.html', data=recommendations, query=user_input)


if __name__ == "__main__":

    app.run(debug=True)  

