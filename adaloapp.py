from flask import Flask, request, jsonify
import requests
import json

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
    
    print(f"Fetching user data from Adalo API for user ID: {user_id}")
    response = requests.get(adalo_api_url, headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"User data retrieved: {user_data}")
        return user_data  # Return user data as JSON
    else:
        print(f"Failed to retrieve user data. Status code: {response.status_code}")
        return {"error": "Failed to retrieve user data", "status_code": response.status_code}

# Function to get all subcategories from Adalo
def get_subcategories():
    adalo_api_url = "https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_2ccd07e119c34eec8fdcb615862c16d7"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("Fetching subcategories from Adalo API")
    response = requests.get(adalo_api_url, headers=headers)
    
    if response.status_code == 200:
        subcategories_data = response.json()
        print(f"Subcategories data retrieved: {subcategories_data}")
        return subcategories_data  # Return subcategories data as JSON
    else:
        print(f"Failed to retrieve subcategories. Status code: {response.status_code}")
        return {"error": "Failed to retrieve subcategories", "status_code": response.status_code}

# Function to update user's "PracticeBase" and "Today" with post IDs
def update_user_posts(user_id, practice_base, today):
    adalo_api_url = f"https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_4d891624fa3c4f86b4bce06a08b6ec93/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Ensure practice_base and today are lists
    if not isinstance(practice_base, list):
        practice_base = [practice_base]
    
    if not isinstance(today, list):
        today = [today]
    
    # Manually create the JSON payload as a string to match Postman behavior
    payload_string = json.dumps({
        "PraticeBase": practice_base,
        "Today": today
    })
    
    print(f"Payload string being sent: {payload_string}")
    
    response = requests.put(adalo_api_url, headers=headers, data=payload_string)  # Using 'data' instead of 'json'
    
    if response.status_code == 200:
        updated_user_data = response.json()
        print(f"User data updated successfully: {updated_user_data}")
        return updated_user_data  # Return updated user data as JSON
    else:
        print(f"Failed to update user data. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return {"error": "Failed to update user data", "status_code": response.status_code}

@app.route('/fetch_user_and_update_posts', methods=['POST'])
def fetch_user_and_update_posts():
    try:
        # Get the user ID from Adalo's request
        user_id = request.json.get('user_id')
        
        if not user_id:
            print("Error: User ID not provided")
            return jsonify({"error": "User ID not provided"}), 400
        
        # Step 1: Fetch user data from Adalo API
        print(f"Step 1: Fetching user data for user ID: {user_id}")
        user_data = get_user_data_from_adalo(user_id)
        if 'error' in user_data:
            return jsonify(user_data), user_data.get("status_code", 500)
        
        # Step 2: Fetch all subcategories
        print("Step 2: Fetching all subcategories")
        subcategories_data = get_subcategories()
        if 'error' in subcategories_data:
            return jsonify(subcategories_data), subcategories_data.get("status_code", 500)
        
        # Step 3: Extract all post IDs from subcategories
        all_post_ids = []
        subcategories = subcategories_data.get('records', [])
        print(f"Subcategories records: {subcategories}")
        for subcategory in subcategories:
            posts = subcategory.get('Posts', [])
            print(f"Posts in subcategory {subcategory.get('id')}: {posts}")
            all_post_ids.extend(posts)
        
        print(f"All post IDs collected: {all_post_ids}")
        
        # Step 4: Update user's "PracticeBase" and "Today" with all post IDs
        print(f"Step 4: Updating user {user_id} PracticeBase and Today with post IDs")
        updated_user_data = update_user_posts(user_id, all_post_ids, all_post_ids)
        if 'error' in updated_user_data:
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)
        
        # Return the updated user data
        print(f"User {user_id} updated successfully")
        return jsonify(updated_user_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/base-reset', methods=['POST'])
def base_reset():
    try:
        # Get the user ID and current subcategory ID from the request
        user_id = request.json.get('user_id')
        subcategory_id = request.json.get('subcategory_id')
        
        if not user_id or not subcategory_id:
            print("Error: User ID or Subcategory ID not provided")
            return jsonify({"error": "User ID or Subcategory ID not provided"}), 400

        # Step 1: Fetch user data from Adalo API
        print(f"Fetching user data for user ID: {user_id}")
        user_data = get_user_data_from_adalo(user_id)
        if 'error' in user_data:
            return jsonify(user_data), user_data.get("status_code", 500)

        # Step 2: Fetch all subcategories
        print(f"Fetching subcategories to find subcategory with ID: {subcategory_id}")
        subcategories_data = get_subcategories()
        if 'error' in subcategories_data:
            return jsonify(subcategories_data), subcategories_data.get("status_code", 500)

        # Step 3: Find the specified subcategory and get its posts
        subcategories = subcategories_data.get('records', [])
        subcategory = next((sc for sc in subcategories if sc.get('id') == subcategory_id), None)

        if not subcategory:
            print(f"Error: Subcategory with ID {subcategory_id} not found")
            return jsonify({"error": "Subcategory not found"}), 404

        # Get posts from PracticeDone in the subcategory
        practice_done_posts = subcategory.get('PracticeDone', [])
        
        if not practice_done_posts:
            print(f"No PracticeDone posts found for subcategory {subcategory_id}")
            return jsonify({"message": "No PracticeDone posts found"}), 200

        # Step 4: Update user's PracticeBase with posts from PracticeDone
        print(f"Updating user {user_id} PracticeBase with posts from PracticeDone in subcategory {subcategory_id}")
        updated_user_data = update_user_posts(user_id, practice_done_posts, [])
        if 'error' in updated_user_data:
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)

        # Return the updated user data
        print(f"User {user_id} updated successfully with PracticeDone posts from subcategory {subcategory_id}")
        return jsonify(updated_user_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
