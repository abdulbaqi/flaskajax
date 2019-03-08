from app import db, Country
db.create_all()


import pandas as pd
cc = pd.read_csv('data/country_codes.csv', encoding='utf-8')

for index,row in cc.iterrows():
    if row[2]!='x':
    	addcc = Country(name=row[1], iso=row[0])
    	db.session.add(addcc)
    	db.session.commit()
