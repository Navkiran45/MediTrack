from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class MongoDBHelper:
    def __init__(self, collection = "users"):

        uri = "mongodb+srv://navkirank45:0811@cluster0.jeauydu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        self.db = client['training']
        self.collection = self.db[collection]

    # query as input will act as condition
    # what to delete, what to fetch, what to update 

    def insert(self, document):
        result = self.collection.insert_one(document)
        print("Document inserted in the ", self.collection.name)
       # print("Result is: ",result, result.inserted_id)
        print("Result is: ",result)
        return result
    
    def fetch(self, query=""):
        documents = self.collection.find(query)
        return list(documents)

    def delete(self,query=""):
        result = self.collection.delete_one(query)
        print("Result is: ", result)
        return result

    def update(self,document, query):
        document_to_update = {'$set': document}
        result = self.collection.update_one(query, document_to_update)
        print("result is:", result)
        return result
