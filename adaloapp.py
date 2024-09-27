from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Function to get user data from Adalo using the provided user_id
def get_user_data_from_adalo(user_id):
    # Your Adalo API URL with the user_id
    adalo_api_url = f"https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_4d891624fa3c4f86b4bce06a08b6ec93/{user_id}"
    
    # Make the request to Adalo API
    headers = {
        'Authorization': 'Bearer YOUR_ADALO_API_KEY',  # Replace with your Adalo API key
        'Content-Type': 'application/json'
    }
    
    response = requests.get(adalo_api_url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return the user data as JSON
    else:
        return {"error": "Failed to retrieve user data", "status_code": response.status_code}

# API endpoint to be called from Adalo
@app.route('/fetch_user', methods=['POST'])
def fetch_user():
    try:
        # Get the user ID from Adalo's request
        user_id = request.json.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID not provided"}), 400
        
        # Fetch user data from Adalo API
        user_data = get_user_data_from_adalo(user_id)
        
        # Return the user data
        return jsonify(user_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
