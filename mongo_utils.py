from pymongo import MongoClient

class mongo_utils:
    def __init__(self, uri, db_name):
        self.client, self.db = self.connect_to_mongodb(uri, db_name)

    def connect_to_mongodb(self, uri, db_name):
        """Connect to the MongoDB and return the client and database objects."""
        client = MongoClient(uri)
        db = client[db_name]
        return client, db

    def query_data(self, collection, pipeline):
        """Query data from the given collection based on the provided pipeline."""
        return collection.aggregate(pipeline)

    # Aggregation pipeline -  top-10 most popular keywords 
    aggregation_pipeline = [
        {
            "$match": {
                "keywords": { "$elemMatch": { "name": { "$exists": True } } }
            }
        },
        {
            "$unwind": "$keywords"
        },
        {
            "$group": {
                "_id": "$keywords.name",
                "count": { "$sum": 1 }
            }
        },
        {
            "$sort": { "count": -1 }
        },
        {
            "$limit": 10
        }
    ]

    # Method to execute the aggregation query
    def execute_query(self):
        faculty_collection = self.db['publications']
        return self.query_data(faculty_collection, self.aggregation_pipeline)






        


