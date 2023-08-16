import mysql.connector as connector
import pandas as pd

class mysql_utils:
    def __init__(self, host, user, password, database):
        self.cnx = connector.connect(host=host, user=user, password=password,
                                     database=database)
    
        self.cursor = self.cnx.cursor()

        # create new table for keyword watchlist with Constraints
        self.createTableQuery = ("CREATE TABLE IF NOT EXISTS fav_keyword ("
                                 "id INT, "
                                 "name VARCHAR(512), "
                                 "PRIMARY KEY (id), "
                                 "FOREIGN KEY (id) REFERENCES keyword(id));")
        self.cursor.execute(self.createTableQuery)
        self.cursor.execute('commit')

        # create View to store keyword name and publication id, which will be used in multiple functions
        self.createView = ("CREATE OR REPLACE VIEW publication_keyword_name AS "
                           "SELECT publication_keyword.publication_id AS publication_id, keyword.name AS keyword_name FROM "
                           "publication_keyword, keyword WHERE publication_keyword.keyword_id = keyword.id;")
        self.cursor.execute(self.createView)
        self.cursor.execute('commit')

        # create Prepared Statement to retrieve favourite keyword names, which will be used in multiple functions
        self.createPreparedStmt = ("PREPARE get_fav_keyword_name FROM 'SELECT name FROM fav_keyword';")
        self.cursor.execute(self.createPreparedStmt)
        self.cursor.execute('commit')

    def get_top_university_by_keyword(self, keyword):
        dataSQL = []
        query = ("SELECT university.name, top_university.faculty_count FROM university," 
                    "(SELECT university_id, COUNT(id) AS faculty_count FROM faculty WHERE id IN "
                    "(SELECT faculty_id FROM faculty_keyword WHERE keyword_id IN "
                    "(SELECT id FROM keyword WHERE name = %s)) "
                    "GROUP BY university_id "
                    "ORDER BY faculty_count DESC LIMIT 10)top_university "
                    "WHERE university.id = top_university.university_id")

        if keyword != '':
            self.cursor.execute(query, (keyword,))
            rows = self.cursor.fetchall()

            data = pd.DataFrame(columns=['university', 'faculty'])
            for row in rows:
                dataSQL.append(list(row))
                labels = ['university', 'faculty']
                data = pd.DataFrame.from_records(dataSQL, columns=labels)
                data = data.to_dict('records')
        else:
            data = pd.DataFrame(columns=['university', 'faculty'])

        return data

    def add_fav_keyword(self, keyword):
        insertQuery = ("INSERT INTO fav_keyword (id, name) SELECT "
                        "(SELECT id FROM keyword WHERE name = %s), %s WHERE "
                        "(NOT EXISTS (SELECT * FROM fav_keyword WHERE name = %s)) AND "
                        "((SELECT COUNT(fav_keyword.name) FROM fav_keyword) < 5) AND "
                        "((SELECT id FROM keyword WHERE name = %s) IS NOT NULL)")
        if keyword != '':
            self.cursor.execute(insertQuery, (keyword, keyword, keyword, keyword))
            self.cursor.execute('commit')
        showQuery = ("EXECUTE get_fav_keyword_name")
        self.cursor.execute(showQuery)

        records = self.cursor.fetchall()
        labels = ['keyword']
        if not records:
            data = pd.DataFrame(columns=labels)
        else:
            data = pd.DataFrame(data=records, columns=labels)

        return data

    def show_fav_keyword(self):
        showQuery = ("EXECUTE get_fav_keyword_name")
        self.cursor.execute(showQuery)
        records = self.cursor.fetchall()

        labels = ['keyword']
        if not records:
            data = pd.DataFrame(columns=labels)
        else:
            data = pd.DataFrame(data=records, columns=labels)

        return data

    def get_fav_keyword_dropdown(self):
        showQuery = ("EXECUTE get_fav_keyword_name")
        self.cursor.execute(showQuery)
        records = self.cursor.fetchall()

        if not records:
            data = []
        else:
            data = []
            for row in records:
                data.append(row[0])
        return data

    def remove_fav_keyword(self, keyword):
        removeQuery = ("DELETE FROM fav_keyword WHERE name = %s")
        if keyword != '':
            self.cursor.execute(removeQuery, (keyword,))
            self.cursor.execute('commit')
        showQuery = ("EXECUTE get_fav_keyword_name")
        self.cursor.execute(showQuery)
        records = self.cursor.fetchall()

        labels = ['keyword']
        if not records:
            data = pd.DataFrame(columns=labels)
        else:
            data = pd.DataFrame(data=records, columns=labels)

        return data

    def get_fav_keyword_trend(self):

        getQuery = ("SELECT fav_keyword.name, publication.year, COUNT(publication.id) FROM "
                    "publication_keyword_name, publication, fav_keyword WHERE "
                    "publication_keyword_name.keyword_name = fav_keyword.name AND "
                    "publication.id = publication_keyword_name.publication_id "
                    "GROUP BY publication.year, fav_keyword.name ORDER BY publication.year")

        self.cursor.execute(getQuery)
        records = self.cursor.fetchall()

        labels = ['keyword', 'year', 'count']
        if not records:
            data = pd.DataFrame(columns=labels)
        else:
            data = pd.DataFrame(data=records, columns=labels)

        return data

    def get_related_keyword(self, keyword):

        getQuery = ("SELECT keyword.name, COUNT(publication_keyword.publication_id) AS count_publication "
                    "FROM keyword, publication_keyword, "
                    "(SELECT publication_id FROM publication_keyword_name WHERE keyword_name = %s) "
                    "AS related_publication WHERE keyword.id = publication_keyword.keyword_id AND "
                    "related_publication.publication_id = publication_keyword.publication_id AND "
                    "keyword.name != %s GROUP BY keyword.name ORDER by count_publication DESC LIMIT 10")

        if keyword != '':
            self.cursor.execute(getQuery, (keyword, keyword))
        records = self.cursor.fetchall()

        labels = ['keyword', 'no. of shared publications']
        if not records:
            data = pd.DataFrame(columns=labels)
        else:
            data = pd.DataFrame(data=records, columns=labels)

        return data
        
    def get_related_keyword_dropdown(self, keyword):
        getQuery = ("SELECT keyword.name, COUNT(publication_keyword.publication_id) AS count_publication "
                    "FROM keyword, publication_keyword, "
                    "(SELECT publication_id FROM publication_keyword_name WHERE keyword_name = %s) "
                    "AS related_publication WHERE keyword.id = publication_keyword.keyword_id AND "
                    "related_publication.publication_id = publication_keyword.publication_id AND "
                    "keyword.name != %s GROUP BY keyword.name ORDER by count_publication DESC LIMIT 10")
        if keyword != '':
            self.cursor.execute(getQuery, (keyword, keyword))
        records = self.cursor.fetchall()

        if not records:
            data = []
        else:
            data = []
            for row in records:
                data.append(row[0])
        return data

