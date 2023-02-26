import sqlite3

# create a connection to the database for writing on it
conct = sqlite3.connect('instance/database.db')

# create a cursor create a table, insert table, ... with using the upper connection (conct)
crsr = conct.cursor()

# # create a table for the fitness programs
# crsr.execute(""" CREATE TABLE fitnessprograms (
#     excersiegoal TEXT,
#     programname TEXT
# )
# """)

# all_programs_input = [
#     ('Being Healthy', 'Walk'),
#     ('Build Muscle', 'Full Body'),
#     ('Increase Stamina', 'Run'),
# ]

# # insert data to table
# crsr.executemany(" INSERT INTO fitnessprograms VALUES (?, ?)", all_programs_input)

crsr.execute("SELECT programname FROM fitnessprograms WHERE excersiegoal = 'Build Muscle'")

# to create and apply changes we to use "commit"
conct.commit()

# closing the connection
conct.close()