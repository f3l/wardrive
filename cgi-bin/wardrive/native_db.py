#!/usr/bin/env python

"""Experiments in providing native Python access using basic Python
types.

The native interface is intended to be a pure Python interface to
access datases, although in a restricted fashion.
http://mysqlmusings.blogspot.com/2011/09/python-interface-to-mysql.html
https://launchpad.net/myconnpy
"""

import mysql.connector
import mysql.connector.cursor
import mysql.connector.errors

_SELECT_FRM = "SELECT {0} FROM {1} WHERE {2}"
_INSERT_FRM = "INSERT INTO {0} SET {1}"
_DELETE_FRM = "DELETE FROM {0} WHERE {1}"
_UPDATE_FRM = "UPDATE {0} SET {1} WHERE {2}"

_SQL_TYPE = {
	int: (lambda s: 'INT'),
	str: (lambda s: 'TEXT'),
	long: (lambda s: 'LONG'),
	float: (lambda s: 'FLOAT'),
	bool: (lambda s: 'BIT(1)'),
	}

class _DictCursor(mysql.connector.cursor.MySQLCursor):
	"Cursor that returns a dictionary instead of a tuple."
	def fetchone(self):
		"""Fetch one row from the cursor and return it as a dictionary
		instead of a tuple.
		"""
		row = self._fetch_row()
		if row:
			return dict(zip(self.column_names, self._row_to_python(row)))
		return None

class _DictCursorBuffered(_DictCursor, mysql.connector.cursor.MySQLCursorBuffered):
	pass

mysql.connector.cursor.MySQLCursorBuffered = _DictCursorBuffered

class _MySQLWorker(object):
	"""Base class for objects that work with the MySQL server.
	"""
	def __init__(self, server):
		self.server = server
		self.converter = server.converter

	def _param(self, value):
		value = self.converter.to_mysql(value)
		value = self.converter.escape(value)
		value = self.converter.quote(value)
		return value

	def eq_pair(self, key, value):
		"""Convert a variable-value pair to a comparison string for
		use in an SQL statement.
		"""
		return "`{0}` = {1}".format(key, self._param(value))

	def execute(self, sql, cursor_class=None):
		cur = self.server.connection.cursor()
		cur.execute(sql)
		return cur
        
    
class Where(_MySQLWorker):
	"""Represent the WHERE part of a SELECT or UPDATE.
	"""
	def __init__(self, server, condition):
		super(Where, self).__init__(server)
		self.condition = condition

	def sql(self):
		if isinstance(self.condition, basestring):
			where = self.condition
		else:
			conds = [self.eq_pair(*i) for i in self.condition.items()]
			if len(conds) == 0:
				conds = ['1']
			where = ' AND '.join(conds)
		return where

class Assign(_MySQLWorker):
	"""Represents the assignment part of an INSERT or UPDATE.
	"""
	def __init__(self, server, fields):
		super(Assign, self).__init__(server)
		self.fields = fields

	def sql(self):
		assign = [ self.eq_pair(*i) for i in self.fields.items() ]        
		return ', '.join(assign)

class Select(_MySQLWorker):
	"""Representation of a SELECT done on a database.
	"""
	def __init__(self, table, condition, fields, order):
		super(Select, self).__init__(table.database.server)
		self.table = table
		self.fields = fields
		self.order = order
		if isinstance(condition, Where):
			self.condition = condition
		else:
			self.condition = Where(table.database.server, condition)

	def count(self):
		"""Count the number of rows instead of getting the rows.

		Note that a new object is returned.
		"""
		return Count(self.table, self.condition, self.order)

	def sort(self, keys):
		return Select(self.table, self.condition, self.fields, keys)


	def _order_pair(self, key, value):
		if value >= 0:
			return "`{0}` ASC".format(key)
		if value < 0:
			return "`{0}` ASC".format(key)

	def sql(self):
		"""Build the SELECT statement.
		"""
		# Build the fields text for the query
		if isinstance(self.fields, basestring):
			fields = self.fields
		else:
			fields = ','.join(self.fields)

		stmt = _SELECT_FRM.format(fields, self.table.name, self.condition.sql())

		# Build the ORDERED BY part for the statement
		if self.order:
			orders = [self._order_pair(*i) for i in self.order.items()]
			stmt += " ORDER BY " + ','.join(orders)
		return stmt

	def __iter__(self):
		"""Create an iterator over the rows of the select.

		This function will create a cursor for the select by creating
		the select from the information in the object, creating a
		cursor for the database connection, and executing the query.

		The cursor for the result will be returned.
		"""
		# Create a cursor and execute the statement. This will return
		# the cursor, which is iterable.
		conn = self.server.connection
		conn.set_database(self.table.database.name)
		cur = conn.cursor(cursor_class=_DictCursor)
		cur.execute(self.sql())
		return cur

class Count(Select):
	def __init__(self, table, condition, order):
		super(Count, self).__init__(table, condition,	"COUNT(*) as `count`", order)

	def __int__(self):
		self.server.connection.set_database(self.table.database.name)
		return self.execute(self.sql()).next()[0]

	def __str__(self):
		return str(int(self))

class Call(_MySQLWorker):
	"""Representation of a CALL done on a database.
	"""
	def __init__(self, database, procname, args=()):
		super(Call, self).__init__(database.server)
		self.database = database
		self.procname = procname
		self.args = args

	def __iter__(self):
		"""Create an iterator over the rows of the CALL.

		This function will create a cursor for the select by creating
		the select from the information in the object, creating a
		cursor for the database connection, and executing the query.

		The cursor resultset for the result will be returned.
		"""
		# Create a cursor and execute the statement. This will return
		# the cursor resultset, which is iterable.
		conn = self.server.connection
		conn.set_database(self.database.name)
		cur = conn.cursor(cursor_class=_DictCursor)
		cur.callproc(self.procname, self.args)
		return cur.next_proc_resultset()

class Table(_MySQLWorker):
	"""A table in a database.
	"""
	def __init__(self, database, name):
		super(Table, self).__init__(database.server)
		self.database = database
		self.name = name

	def find(self, cond, fields=["*"]):
		return Select(self, cond, fields, {})

	def _insert(self, document):
		assign = Assign(self.server, document)
		stmt = _INSERT_FRM.format(self.name, assign.sql())
		self.server.connection.set_database(self.database.name)
		self.execute(stmt)

	def _create_pair(self, var_name, sample_value):
		mapper = _SQL_TYPE[type(sample_value)]
		return "`{0}` {1}".format(var_name, mapper(sample_value))

	def _create(self, document):
		fields = [ self._create_pair(*i) for i in document.items() ]
		stmt = "CREATE TABLE {0} ({1})".format(self.name, ','.join(fields))
		self.server.connection.set_database(self.database.name)
		self.execute(stmt)

	def insert(self, document):
		try:
			self._insert(document)
		except mysql.connector.errors.ProgrammingError as details:
			if details.errno == 1146:
				self._create(document)
				self._insert(document)
			else:
				raise

	def update(self, cond, update):
		where = Where(self.server, cond)
		assign = Assign(self.server, update)
		stmt = _UPDATE_FRM.format(self.name, assign.sql(), where.sql())
		self.server.connection.set_database(self.database.name)
		self.execute(stmt)

	def delete(self, keys):
		where = Where(self.server, keys)
		stmt = _DELETE_FRM.format(self.name, where.sql())
		self.server.connection.set_database(self.database.name)
		self.execute(stmt)

class Database(_MySQLWorker):
	"""A database on object on a server containing tables.
	"""
	def __init__(self, server, name):
		super(Database, self).__init__(server)
		self.name = name

	def table(self, table):
		return Table(self, table)

	def call(self, procname, args=()):
		return Call(self, procname, args)

	def __getattr__(self, table):
		return self.table(table)

class Server(object):
	"""A server connection.
	Call: Server(host, user, passwd)
	"""
	def __init__(self, **kwrds):
		kwrds.setdefault('autocommit', True)
		self.connection = mysql.connector.connect(**kwrds)
		self.converter = self.connection.converter

	def database(self, name):
		return Database(self, name)

	def __getattr__(self, name):
		return self.database(name)

"""
if __name__ == '__main__':
    server = Server(host='127.0.0.1')

    server.test.t1.insert({'more': 3, 'magic': 'just a test'})
    server.test.t1.insert({'more': 3, 'magic': 'just another test'})
    server.test.t1.insert({'more': 4, 'magic': 'quadrant'})
    server.test.t1.insert({'more': 5, 'magic': 'even more magic'})
    for row in server.test.t1.find({}):
        print row
    for row in server.test.t1.find({'more': 3}):
        print "The magic is:", row['magic']
    for row in server.test.t1.find("more = 3"):
        print row
    for row in server.test.t1.find("more = 3", ['magic']):
        print row
    for row in server.test.t1.find({}).sort({ 'more': -1 }):
        print row
    
    print "Count:", server.test.t1.find({ 'more': 3, }).count()
    server.test.options.insert({
            'file': 'foo.txt',
            'opt': '--magic'
            })

    server.test.t1.update({'more': 3}, {'magic': 'no magic'})

    server.test.t1.delete({ 'more': 3, })
    server.test.t1.delete({ 'more': 4, })
    server.test.t1.delete({ 'more': 5, })
    server.test.options.delete({ 'file': 'foo.txt', })
    server.test.options.delete({ 'file': 'bar.txt', })
"""
