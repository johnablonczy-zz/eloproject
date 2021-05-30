from datetime import datetime
from functools import reduce
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Elo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if(request.method == 'POST'):
        elo_name = request.form['name']
        elo_score = request.form['score']
        new_elo = Elo(score = elo_score, name = elo_name )

        try:
            db.session.add(new_elo)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem adding your elo'
            
    else:
        all_elos = Elo.query.order_by(-(Elo.score)).all()
        return render_template('index.html', elos = all_elos)

@app.route('/delete/<int:id>')
def delete(id):
    elo_to_delete = Elo.query.get_or_404(id)

    try:
        db.session.delete(elo_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting this elo'

@app.route('/update_elos/', methods=['POST', 'GET'])
def update_elos():
    names = request.form.getlist('name')
    places = request.form.getlist('place')
    old_scores = []
    for name in names:
        score = Elo.query.filter_by(name=name).first().score
        old_scores.append(score)
    
    for i in range(len(names)):
        elo_sum = 0
        for j in range(len(names)):
            isWin = 0
            if j != i:
                if places[i] < places[j]:
                    isWin = 1
                expected = 1/(1 + pow(10, (old_scores[j]-old_scores[i])/400))
                elo_sum += old_scores[i]+32*(isWin - expected)
                
        Elo.query.filter_by(name=names[i]).first().score = int(elo_sum/(len(names)-1))

    db.session.commit()

    return redirect('/')
    
if __name__ == "__main__":
    app.run(debug=True)