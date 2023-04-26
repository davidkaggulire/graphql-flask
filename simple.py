from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from ariadne.explorer import ExplorerGraphiQL
from flask import Flask, request, jsonify
from ariadne import gql, QueryType, make_executable_schema, graphql_sync, MutationType

# Define type definitions (schema) using SDL
type_defs = gql(
   """
   type Query {
       places: [Place]
   }


   type Place {
       name: String!
       description: String!
       country: String!
       }  

   type Mutation{add_place(name: String!, description: String!, country: String!): Place}
   """
)

# Initialize query

query = QueryType()

# Initialize mutation

mutation = MutationType()

# Define resolvers
# places resolver (return places )
@query.field("places")
def places(*_):
#    return places
    return [place.to_json() for place in Places.query.all()]


# place resolver (add new  place)

# sample mutation
# mutation {
#   add_place(name: "kilimanjaro", description: "highest mountain in africa", country:"tanzania"){
#     name
#   }
# }
@mutation.field("add_place")
def add_place(_, info, name, description, country):
#    places.append({"name": name, "description": description, "country": country})
#    return {"name": name, "description": description, "country": country}
    place = Places(name=name, description=description, country=country)
    place.save()
    return place.to_json()

# Create executable schema
schema = make_executable_schema(type_defs, [query, mutation])

# initialize flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Places(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(80), nullable=False)
   description = db.Column(db.String(255), nullable=False)
   country = db.Column(db.String(80), nullable=False)

   def to_json(self):
       return {
           "name": self.name,
           "description": self.description,
           "country": self.country,
       }

   def save(self):
       db.session.add(self)
       db.session.commit()

explorer_html = ExplorerGraphiQL().html(None)

# Create a GraphQL Playground UI for the GraphQL schema
@app.route("/graphql", methods=["GET"])
def graphql_playground():
   # Playground accepts GET requests only.
   # If you wanted to support POST you'd have to
   # change the method to POST and set the content
   # type header to application/graphql
   return explorer_html, 200

# Create a GraphQL endpoint for executing GraphQL queries
@app.route("/graphql", methods=["POST"])
def graphql_server():
   data = request.get_json()
   success, result = graphql_sync(schema, data, context_value={"request": request})
   status_code = 200 if success else 400
   return jsonify(result), status_code

# Run the app
if __name__ == "__main__":
#    places = [
#        {"name": "Paris", "description": "The city of lights", "country": "France"},
#        {"name": "Rome", "description": "The city of pizza", "country": "Italy"},
#        {
#            "name": "London",
#            "description": "The city of big buildings",
#            "country": "United Kingdom",
#        },
#    ]
   app.run(debug=True)