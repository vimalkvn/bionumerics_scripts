"""PostgreSQL functions"""
import pyodbc

DATABASE = "cherry_picking"

user, password = ("user", "password")
DSN = ("Driver={PostgreSQL ANSI};Server=localhost;Port=5432;Database=%s;"
"Uid=%s;Pwd=%s;" % (DATABASE, user, password))


def connect():
	"""Returns a connection"""
	try:
		connection = pyodbc.connect(DSN)
	except:
		raise
	return connection


def get_data(db):
	"""Get all data from cherry_picking database for the current BN database"""
	result = []
	conn = connect()
	cursor = conn.cursor()
	sql = ("select key, gene, orientation, username, status from traces where "
			"database=? order by key, gene, orientation")
	data = (db, )
	try:
		cursor.execute(sql, data)
		result = cursor.fetchall()
	except:
		raise
	finally:
		cursor.close()
		conn.close()

	return result

if __name__ == "__main__":
	database = "testDB"
	res = get_data(database)
	print res
