from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Adalo API key (replace with your actual API key)
ADALO_API_KEY = 'ae1vdlouhuan5442p2z1wvgd4'

# Function to get user data from Adalo using the provided user_id
def get_user_data_from_adalo(user_id):
    adalo_api_url = f"https://api.adalo.com/v0/apps/a97d4de8-d373-4c8f-ba84-86930bc15a00/collections/t_96cd42bdae754d8abf7f2cb6680040c6/{user_id}"
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
    adalo_api_url = "https://api.adalo.com/v0/apps/a97d4de8-d373-4c8f-ba84-86930bc15a00/collections/t_a7f8c77d7e2146bfb1ab29fa377dce90"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(adalo_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return subcategories data as JSON
    else:
        return {"error": "Failed to retrieve subcategories", "status_code": response.status_code}

# Function to update user's fields (PracticeBase, Today, and Level1Post)
def update_user_fields(user_id, today, level1_post, practice_base):
    adalo_api_url = f"https://api.adalo.com/v0/apps/a97d4de8-d373-4c8f-ba84-86930bc15a00/collections/t_96cd42bdae754d8abf7f2cb6680040c6/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "Today": today,
        "Level1Post": level1_post,
        "PracticeBase": practice_base
    }
    
    response = requests.put(adalo_api_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json()  # Return updated user data as JSON
    else:
        return {"error": "Failed to update user data", "status_code": response.status_code}

@app.route('/start', methods=['PATCH'])
def combined_reset():
    try:
        # Get the user ID and subcategory ID from the request
        user_id = request.json.get('user_id')
        subcategory_id = request.json.get('subcategory_id')
        
        if not user_id or not subcategory_id:
            return jsonify({"error": "User ID or Subcategory ID not provided"}), 400

        # Step 1: Fetch user data from Adalo API
        user_data = get_user_data_from_adalo(user_id)
        if 'error' in user_data:
            return jsonify(user_data), user_data.get("status_code", 500)

        # Step 2: Fetch all subcategories
        subcategories_data = get_subcategories()
        if 'error' in subcategories_data:
            return jsonify(subcategories_data), subcategories_data.get("status_code", 500)

        # Step 3: Find the specified subcategory and get its posts
        subcategories = subcategories_data.get('records', [])
        subcategory = next((sc for sc in subcategories if str(sc.get('id')) == str(subcategory_id)), None)

        if not subcategory:
            return jsonify({"error": "Subcategory not found"}), 404

        # Get all posts from the subcategory
        posts_to_add = subcategory.get('Posts', [])
        
        if not posts_to_add:
            return jsonify({"message": "No posts found"}), 200

        # Step 4: Update user's PracticeBase, Today, and Level1Post fields
        existing_practice_base = user_data.get('PracticeBase', [])
        existing_today = user_data.get('Today', [])
        existing_level1_post = user_data.get('Level1Post', [])

        updated_practice_base = list(set(existing_practice_base + posts_to_add))
        updated_today = list(set(existing_today + posts_to_add))
        updated_level1_post = list(set(existing_level1_post + posts_to_add))

        updated_user_data = update_user_fields(user_id, updated_today, updated_level1_post, updated_practice_base)
        if 'error' in updated_user_data:
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)

        return jsonify(updated_user_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
