"""Tests for sqlite support

Takes database as argument.

1. If database is absent, create table traces
2. If database exists, connect and check if traces table exists
3. Execute success
4. Execute failure
"""

import os
import sys
sys.path.insert(0, "../")
SCRIPT_PATH = r"C:\Users\vimal\Workspace\itcrispr"
sys.path.append(SCRIPT_PATH)
import unittest
from itcrispr import dbms

DATADIR = os.path.join(SCRIPT_PATH, "itcrispr", "tests", "data")
DB = os.path.join(DATADIR, "db.sqlite")
sys.stderr = open(os.path.join(DATADIR, "test_sqlite.txt"), "w")


class TestSqlite(unittest.TestCase):

    def setUp(self):
        if os.path.exists(DB):
            os.remove(DB)

    def testCreateTable(self):
        """If database is new, create traces table and return status T/F."""
        created = dbms.create_traces_table(DB)
        self.assertTrue(created)

    def testCheckTableExists(self):
        """If database exists, connect and check if traces table exists."""
        # create a dummy table
        con, cur = dbms.connect(DB)
        cur.execute("create table traces(id int)")
        con.commit()
        con.close()
        # don't create it again
        created = dbms.create_traces_table(DB)
        self.assertFalse(created)

    def testSaveFinished(self):
        """Save new entry as finished"""
        dbms.create_traces_table(DB)
        con, cur = dbms.connect(DB)

        key, gene = ("PS48104-1", "CRISPR1")
        # entry does not exist
        cur.execute("select id from traces where key=? and gene=?",
                    (key, gene))
        self.assertEqual(len(cur.fetchall()), 0)

        # save as finished
        cur.execute("insert into traces(key, gene, status) values (?, ?, ?)",
                    (key, gene, "Finished"))

        # check only 1 entry exists
        cur.execute("select count(*) from traces where key=? and gene=?",
                    (key, gene))
        self.assertEqual(cur.fetchone()[0], 1)
        con.commit()
        con.close()

#    def testExportDatabase(self):
#        dbms.create_traces_table(DB)
#        con, cur = dbms.connect(DB)
#
#        data = ((1, "P548104-0", "CRISPR1", "vimal",
#                 "vimal", "2012-07-30 11:15:40", "Finished", ""),
#        (2, "MC-05-0618", "CRISPR1", "vimal",
#         "vimal", "2012-07-30 11:22:32", "Finished", ""),
#        (3, "MC-05-0618", "CRISPR2", "vimal",
#         "vimal", "2012-07-30 11:45:25", "Finished", ""),
#        (4, "MC-04-0525", "CRISPR1", "vimal",
#         "vimal", "2012-07-30 11:48:37", "Finished", ""),
#        (5, "84237156229", "CRISPR1", "vimal",
#         "vimal", "2012-07-30 13:31:55", "Repeat", "STM4-F"),
#        (6, "84237156229", "CRISPR1", "vimal",
#         "vimal", "2012-07-30 13:31:55", "Repeat", "STM10-F"),
#        (7, "84237156229", "CRISPR1", "vimal",
#         "vimal", "2012-07-30 13:31:55", "Repeat", "STM18-R"),
#        (8, "84237156229", "CRISPR1", "vimal",
#         "vimal", "2012-07-30 13:31:55", "Repeat", "STMB3-F"),
#        (9, "84237156229", "CRISPR1", "vimal",
#         "vimal", "2012-07-30 13:31:55", "Repeat", "STM6-F"))
#
#        sql = ("insert into traces(id, key, gene, database, username, "
#               "date, status, primer) values (?,?,?,?,?,?,?,?)")
#        cur.executemany(sql, data)
#
#        #now do export
#        with open(os.path.join(DATADIR, "traces-export.txt"), "w") as f:
#            cur.execute("PRAGMA table_info(traces)")  # sqlite only
#            cols = cur.fetchall()
#            header = ", ".join([str(col[1]) for col in cols])
#            #
#            data = []
#            for row in cur.execute("select * from traces"):
#                data.append(", ".join(str(item) for item in row))
#
#            if len(data):
#                f.write("{0}\n".format(header))
#                f.write("\n".join(item for item in data))
#
#        con.close()


suite = unittest.TestLoader().loadTestsFromTestCase(TestSqlite)
#suite = unittest.TestSuite()
#suite.addTest(TestSqlite("testExportDatabase"))
unittest.TextTestRunner(stream=sys.stderr, verbosity=3).run(suite)
sys.stderr.flush()
