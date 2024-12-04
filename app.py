from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from supabase_client import supabase

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Serve the home page
@app.route('/')
def home():
    return render_template('venue.html')  # Ensure venue.html is in the templates/ directory

# API to fetch venue images based on venue name
@app.route('/get_venue_images', methods=['GET'])
def get_venue_images():
    venue_name = request.args.get('venue_name')
    try:
        if not venue_name:
            return jsonify({'error': 'Venue name is required.'}), 400

        response = supabase.table("venue-images").select("*").eq("venue_name", venue_name).execute()
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({'message': 'No images found for this venue.'}), 404
    except Exception as e:
        return jsonify({'error': f"Failed to fetch venue images: {str(e)}"}), 500

# API to add a new venue image
@app.route('/add_venue_image', methods=['POST'])
def add_venue_image():
    data = request.json
    try:
        required_fields = ['venue_name', 'section', 'row', 'seat', 'image_url']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

        response = supabase.table("venue-images").insert(data).execute()
        return jsonify({'message': 'Venue image added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': f"Failed to add venue image: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
