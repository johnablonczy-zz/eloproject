from functools import reduce
from operator import add
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wtforms import Form, BooleanField, StringField, validators, IntegerField
from wtforms.fields.core import Field, FieldList, FormField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Elo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return self.name

class EloAddForm(Form):
    name = StringField('Name')
    score = IntegerField('Score')

class PlayerAddForm(Form):
    elos = Elo.query.order_by(-(Elo.score)).all()
    player = QuerySelectField(query_factory=lambda: Elo.query)

added_players = []

class PlaceForm(Form):
    place = SelectField('Place', coerce=int)



@app.route('/', methods=['POST', 'GET'])
def index():
    eloaddform = EloAddForm(request.form)
    playeraddform = PlayerAddForm()
    placeform = PlaceForm()
    placeform.place.choices = list(range(1, len(added_players)+1))
    
    if(request.method == 'POST'):
        elo_name = eloaddform.name.data
        elo_score = eloaddform.score.data
        new_elo = Elo(score = elo_score, name = elo_name )

        try:
            db.session.add(new_elo)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem adding your elo'
            
    else:
        all_elos = Elo.query.order_by(-(Elo.score)).all()
        return render_template('index.html', elos = all_elos, eloaddform = eloaddform, playeraddform = playeraddform, players = added_players, placeform = placeform)

@app.route('/delete/<int:id>')
def delete(id):
    elo_to_delete = Elo.query.get_or_404(id)

    try:
        db.session.delete(elo_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting this elo'

@app.route('/add_player/', methods=['POST', 'GET'])
def add_player():
    playeraddform = PlayerAddForm(request.form)

    if(request.method == 'POST'):
        added_players.append(playeraddform.player.data)
        return redirect('/')

@app.route('/calc_elo/', methods=['POST', 'GET'])
def calc_elo():
    placeform = PlaceForm(request.form)
    game_size = len(added_players)
    places = []
    if(request.method == 'POST'):
        places = list(map(int, request.form.getlist('place')))
        
        for i in range(game_size):
            elo_sum = 0
            for j in range(game_size):
                isWin = 0
                if j != i:
                    if places[i] < places[j]:
                        isWin = 1
                    expected = 1/(1 + pow(10, (added_players[j].score-added_players[i].score)/400))
                    elo_sum += added_players[i].score+32*(isWin - expected)
                    
            Elo.query.filter_by(name=added_players[i].name).first().score = int(elo_sum/(game_size-1))

        db.session.commit()
        added_players.clear()

    return redirect('/')
    
if __name__ == "__main__":
    app.run(debug=True)