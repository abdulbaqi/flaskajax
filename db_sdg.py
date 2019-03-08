from app import db, SDGS
db.create_all()


import pandas as pd
cc = pd.read_csv('data/sdgs_flat.csv', encoding='utf-8')

for index,row in cc.iterrows():
	addcc = SDGS(goal=row[0], 
		ind_desc=row[1], 
		series_type=row[2],
		country_code=row[3],
		country_name=row[4],
		series_desc=row[5],
		frequency = row[6],
		source_type = row[7],
		age_group = row[8],
		location = row[9],
		sex = row[10],
		value_type = row[11],
		unit = row[12],
		unit_multiplier = row[13],
		year = row[14],
		value = row[15]
		)
	db.session.add(addcc)
	db.session.commit()