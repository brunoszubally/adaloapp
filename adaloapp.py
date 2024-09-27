from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Adalo API key (replace with your actual API key)
ADALO_API_KEY = 'e8wk2i21wge6oxz29ye9u9ykr'

# Function to get user data from Adalo using the provided user_id
def get_user_data_from_adalo(user_id):
    adalo_api_url = f"https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_4d891624fa3c4f86b4bce06a08b6ec93/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(adalo_api_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Return user data as JSON
    else:
        return {"error": "Failed to retrieve user data", "status_code": response.status_code}

# Function to get all subcategories from Adalo
def get_subcategories():
    adalo_api_url = "https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_2ccd07e119c34eec8fdcb615862c16d7"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(adalo_api_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Return subcategories data as JSON
    else:
        return {"error": "Failed to retrieve subcategories", "status_code": response.status_code}

# Function to update user's "PracticeBase" with post IDs
def update_user_practice_base(user_id, practice_base):
    adalo_api_url = f"https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_4d891624fa3c4f86b4bce06a08b6ec93/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    # Update the "PracticeBase" field with new post IDs
    payload = {
        "PracticeBase": practice_base
    }
    response = requests.put(adalo_api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()  # Return updated user data as JSON
    else:
        return {"error": "Failed to update user data", "status_code": response.status_code}

@app.route('/fetch_user_and_update_posts', methods=['POST'])
def fetch_user_and_update_posts():
    try:
        # Get the user ID from Adalo's request
        user_id = request.json.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID not provided"}), 400
        
        # Step 1: Fetch user data from Adalo API
        user_data = get_user_data_from_adalo(user_id)
        if 'error' in user_data:
            return jsonify(user_data), user_data.get("status_code", 500)
        
        # Step 2: Fetch all subcategories
        subcategories_data = get_subcategories()
        if 'error' in subcategories_data:
            return jsonify(subcategories_data), subcategories_data.get("status_code", 500)
        
        # Step 3: Extract all post IDs from subcategories
        all_post_ids = []
        subcategories = subcategories_data.get('records', [])
        for subcategory in subcategories:
            posts = subcategory.get('Posts', [])
            all_post_ids.extend(posts)
        
        # Step 4: Update user's "PracticeBase" with all post IDs
        updated_user_data = update_user_practice_base(user_id, all_post_ids)
        if 'error' in updated_user_data:
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)
        
        # Return the updated user data
        return jsonify(updated_user_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
