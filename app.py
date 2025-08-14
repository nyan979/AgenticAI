from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    """
    This is the homepage endpoint. It returns a simple JSON message.
    """
    return jsonify({"message": "Hello, this is a basic API!"})

if __name__ == '__main__':
    # This runs the development server.
    # In a production environment, you would use a more robust server.
    app.run(debug=True)