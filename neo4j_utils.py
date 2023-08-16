from neo4j import GraphDatabase
from py2neo import Graph
import pandas as pd

class neo4j_utils:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def get_top_professor_by_keyword(self, keyword):

        query = ("MATCH (institute:INSTITUTE)<-[affiliate:AFFILIATION_WITH]-(faculty:FACULTY)-[publish:PUBLISH]->"
                 "(publication:PUBLICATION)-[label:LABEL_BY]->(keyword:KEYWORD) WHERE keyword.name = $keyword "
                 "RETURN faculty.name AS faculty_name, institute.name AS university, "
                 "SUM(label.score * publication.numCitations) AS KRC, "
                 "COUNT(publication.id) AS NO_PUBLICATION, SUM(publication.numCitations) AS NO_CITATION "
                 "ORDER BY KRC DESC LIMIT 10")

        labels = ['name', 'university', 'KRC', 'publication count', 'citation count']
        if keyword != '':
            records, summary, keys = self.driver.execute_query(query, keyword=keyword, database_=self.database)
            data = pd.DataFrame(data=records, columns=labels)
        else:
            data = pd.DataFrame(columns=labels)

        return data

        


