from flask import Flask, jsonify, request, redirect
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
CORS(app)
api = Api(app)

# In-memory data storage
items = [
    {"id": 1, "name": "Laptop", "price": 1500},
    {"id": 2, "name": "Phone", "price": 800},
    {"id": 3, "name": "Tablet", "price": 500}
]


# Marshmallow schema for validation
class ItemSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Float(required=True)


item_schema = ItemSchema()

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_DOCS_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_DOCS_URL,
    config={'app_name': "Flask CRUD API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/')
def home():
    """Root endpoint; redirects to Swagger UI."""
    return redirect("/swagger")


class Item(Resource):
    def get(self, item_id=None):
        """
        Get all items or a single item by ID.
        Returns:
            200: Success with items or single item.
            404: If the item_id is provided but not found.
        """
        if item_id:
            item = next((item for item in items if item["id"] == int(item_id)), None)
            if not item:
                return {"message": "Item not found"}, 404
            return {"item": item}, 200
        # Return all items
        return {"items": items}, 200

    def post(self):
        """
        Create a new item.
        Expected JSON: {"name": "string", "price": float}

        Returns:
            201: Item created successfully.
            400: Validation error or bad request.
        """
        try:
            data = item_schema.load(request.get_json())
        except ValidationError as err:
            return {"message": "Invalid input", "errors": err.messages}, 400

        # Auto-increment ID logic
        if items:
            last_id = max(item["id"] for item in items)
            item_id = last_id + 1
        else:
            item_id = 1

        data["id"] = item_id
        items.append(data)
        return {"message": "Item created", "item": data}, 201

    def put(self, item_id):
        """
        Update an existing item by ID.
        Expected JSON: {"name": "string", "price": float}

        Returns:
            200: Item updated.
            404: Item not found.
            400: Validation error.
        """
        existing_item = next((item for item in items if item["id"] == int(item_id)), None)
        if not existing_item:
            return {"message": "Item not found"}, 404

        try:
            data = item_schema.load(request.get_json())
        except ValidationError as err:
            return {"message": "Invalid input", "errors": err.messages}, 400

        existing_item.update(data)
        return {"message": "Item updated", "item": existing_item}, 200

    def delete(self, item_id):
        """
        Delete an item by ID.

        Returns:
            200: Item deleted.
            404: Item not found.
        """
        global items
        item = next((item for item in items if item["id"] == int(item_id)), None)
        if not item:
            return {"message": "Item not found"}, 404
        items = [item for item in items if item["id"] != int(item_id)]
        return {"message": "Item deleted"}, 200


# API Endpoints
api.add_resource(Item, '/items', '/items/<string:item_id>')


@app.route('/static/swagger.json')
def swagger_json():
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Flask CRUD API",
            "description": "A sample API for CRUD operations with validation",
            "version": "1.0.0"
        },
        "host": "localhost:5000",
        "basePath": "/",
        "schemes": ["http"],
        "tags": [
            {
                "name": "Items",
                "description": "Item management operations"
            }
        ],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "paths": {
            "/items": {
                "get": {
                    "tags": ["Items"],
                    "summary": "Get all items",
                    "responses": {
                        "200": {
                            "description": "A list of items",
                            "examples": {
                                "application/json": {
                                    "items": [
                                        {"id": 1, "name": "Laptop", "price": 1500}
                                    ]
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Items"],
                    "summary": "Create a new item",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "price": {"type": "number"}
                                },
                                "required": ["name", "price"]
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Item created"
                        },
                        "400": {
                            "description": "Invalid input"
                        }
                    }
                }
            },
            "/items/{item_id}": {
                "get": {
                    "tags": ["Items"],
                    "summary": "Get a specific item",
                    "parameters": [
                        {
                            "name": "item_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Item details"
                        },
                        "404": {
                            "description": "Item not found"
                        }
                    }
                },
                "put": {
                    "tags": ["Items"],
                    "summary": "Update an item",
                    "parameters": [
                        {
                            "name": "item_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        },
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "price": {"type": "number"}
                                },
                                "required": ["name", "price"]
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Item updated"
                        },
                        "400": {
                            "description": "Invalid input"
                        },
                        "404": {
                            "description": "Item not found"
                        }
                    }
                },
                "delete": {
                    "tags": ["Items"],
                    "summary": "Delete an item",
                    "parameters": [
                        {
                            "name": "item_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Item deleted"
                        },
                        "404": {
                            "description": "Item not found"
                        }
                    }
                }
            }
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
