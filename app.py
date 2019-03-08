from flask import Flask, jsonify, render_template,request, url_for, Response
from flask_sqlalchemy import SQLAlchemy 
import json
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
import pandas as pd

from flask.ext.heroku import Heroku

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY']='my_love_dont_try'
# app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://localhost/sdg'
heroku = Heroku(app)
db = SQLAlchemy(app)

selected_indicators= [
 'Indicator',
 'Unit',
 '2012',
 '2013',
 '2014',
 '2015',
 '2016',
 'Trend',
 ]

class MyForm(FlaskForm):
	sdg = StringField('SDG Goal', validators=[DataRequired(),Length(max=40)],render_kw={"placeholder": "sdg goal"})
	country = StringField('Country', validators=[DataRequired(),Length(max=40)],render_kw={"placeholder": "country"})


class SDG(db.Model):
	__tablename__ = 'sdgs'

	id = db.Column(db.Integer, primary_key=True)
	goal = db.Column(db.String(40), unique=True, nullable = False)

	def __repr__(self):

		return 'Goal {} - {}'.format(self.id, self.goal)

	def as_dict(self):
		# return {c.name: getattr(self, c.name) for c in self.__table__.columns}
		return {'goal': self.goal}

class SDGS(db.Model):
	__tablename__ = 'sdgs_data'

	id = db.Column(db.Integer, primary_key=True)
	goal = db.Column(db.Integer)
	ind_desc = db.Column(db.String(500))
	series_type = db.Column(db.String(2))
	country_code = db.Column(db.String(3))
	country_name = db.Column(db.String(80))
	series_desc = db.Column(db.String(500))
	frequency = db.Column(db.String(10))
	source_type = db.Column(db.String(30))
	age_group = db.Column(db.String(200))
	location = db.Column(db.String(50))
	sex = db.Column(db.String(150))
	value_type = db.Column(db.String(50))
	unit = db.Column(db.String(50))
	unit_multiplier = db.Column(db.String(50))
	year = db.Column(db.Integer)
	value = db.Column(db.Float)


	def __repr__(self):

		return 'Goal {} - {}'.format(self.id, self.goal)

	def as_dict(self):
		# return {c.name: getattr(self, c.name) for c in self.__table__.columns}
		return {'Goal': self.goal, 
		'Indicator Description': self.ind_desc,
		'country': self.country_name, 
		'Series Description': self.series_desc, 
		'Series type': self.series_type,
		'Frequency': self.frequency,
		'Source type': self.source_type,
		'Age group': self.age_group,
		'Location': self.location,
		'Sex': self.sex,
		'Value type': self.value_type,
		'Unit': self.unit,
		'Unit multiplier': self.unit_multiplier,
		'year': self.year, 
		'value': self.value,
		}

class Country(db.Model):
	__tablename__ = 'countries'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), unique=True, nullable = False)
	iso = db.Column(db.String(3), unique=True, nullable = False)


	def __repr__(self):

		return '{} - {}'.format(self.iso, self.name)

	def as_dict(self):
		# return {c.name: getattr(self, c.name) for c in self.__table__.columns}
		return {'name': self.name}


def shorten_list(list_string):
	#this program will remove the starting nulls and ending nulls 
	# from a string containing list of numbers
	# e.g, input [null,2.3,4.5,null,6.5,-12,null,null]
	# output [2.3,4.5,null,6.5,12]
	import re
	#this will detect any numbers
	nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
	# res will contain tuples for each number
	res = [(m.start(0), m.end(0)) for m in re.finditer(nums, list_string)]
	if len(res)>0:
		start = res[0][0]
		end = res[len(res)-1][1]
		return '['+list_string[start:end]+']'
	return '[]'

@app.route('/')
def hello():
	hell = '<b>hello</b> from baqi'
	return render_template('index.html', hell=hell)

@app.route('/sdg')
def sdg():
	form = MyForm()
	goals = SDG.query.all()
	return render_template('sdg.html', goals=goals, form=form)

@app.route('/sdgs')
def sdgdic():
	res = SDG.query.all()
	list_goals = [r.as_dict() for r in res]
	return jsonify(list_goals)

@app.route('/countries')
def countrydic():
	res = Country.query.all()
	list_countries = [r.as_dict() for r in res]
	return jsonify(list_countries)

@app.route('/process', methods=['POST'])
def process():
	sdg = request.form['sdg']
	country = request.form['country']
	goal_number = SDG.query.filter_by(goal=sdg).first()
	goal_number = goal_number.id 
	country_code = Country.query.filter_by(name=country).first()
	country_code = country_code.iso
	if sdg and country:
		pd.set_option('display.max_colwidth', -1)
		qres = SDGS.query.filter_by(goal=goal_number, country_code=country_code).all()
		list_qres = [r.as_dict() for r in qres]
		df = pd.DataFrame(list_qres)
		# df = df.sort_values(['indicator', 'year'])
		df['year'] = df.year.astype(str)
		df = pd.pivot_table(df, values = 'value', index=['Goal',
                                            'country',
                                            'Indicator Description',
                                            'Series type',
                                            'Series Description',
                                            'Frequency',
                                            'Source type',
                                            'Age group',  
                                             'Location', 
        'Sex', 'Value type', 'Unit', 'Unit multiplier'
        ], columns = 'year').reset_index()
		years = df.columns[13:].values.tolist()
		for index, row in df.iterrows():
			ll = row[years].values.tolist()
			llstring = '['+','.join(str(e) for e in ll)+']'
			llstring = llstring.replace('nan','null')
			llstring = shorten_list(llstring)
			llstring = "<canvas class='sparkline' data-chart_values={}></canvas>".format(llstring)
			df.loc[index,'Trend'] = llstring
			df.loc[index,'Indicator'] = '''{} <br><a data-toggle='collapse' href='#ind{}' aria-expanded='false' aria-controls='#ind{}'>More</a><div class='collapse font-weight-light' id='ind{}'><b>Goal</b>:{}<br><b>Country</b>:{}<br><b>Indicator Description:</b>{}<br><b>Series Type:</b>{}<br><b>Frequency:</b>{}<br><b>Source type: </b>{}<br><b>Age group: </b>{}<br><b>Location: </b>{}<br><b>Sex: </b>{}<br><b>Value type:</b> {}<br><b>Unit multiplier:</b> {}</div>'''.format(
				row['Series Description'],
				index,index,index,
				
				row['Goal'],
				row['country'],
				row['Indicator Description'],
				row['Series type'],
				row['Frequency'],
				row['Source type'],
				row['Age group'],
				row['Location'],
				row['Sex'],
				row['Value type'],
				row['Unit'],
				row['Unit multiplier'])
		df = df.loc[:,selected_indicators]
		table = df.to_html(classes=['table', 'table-striped','table_sdg'], index=False, na_rep='..', escape=False, border=0, bold_rows=True, justify='left')
		return jsonify({'df': table})
	return jsonify({'error': 'missing data..'})

if __name__ == '__main__':
	app.run(debug=True)