from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Adalo API key (replace with your actual API key)
ADALO_API_KEY = '4z9ftfskxxeof0i1734i6rr6o'

# Function to get user data from Adalo using the provided user_id
def get_user_data_from_adalo(user_id):
    adalo_api_url = f"https://api.adalo.com/v0/apps/23b040ee-e4d1-4873-bb3b-82e902e29e6d/collections/t_9e358c26e7fc41ad814f0a7a2b5d1265/{user_id}"
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
    adalo_api_url = "https://api.adalo.com/v0/apps/23b040ee-e4d1-4873-bb3b-82e902e29e6d/collections/t_0bb9a402d59f4792afaea12fd9d2928c"
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

# Function to update user's "Today" and "Level1Post" fields with post IDs
def update_user_today_and_level1(user_id, today, level1_post):
    adalo_api_url = f"https://api.adalo.com/v0/apps/23b040ee-e4d1-4873-bb3b-82e902e29e6d/collections/t_9e358c26e7fc41ad814f0a7a2b5d1265/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Ensure today and level1_post are lists
    if not isinstance(today, list):
        today = [today]
    
    if not isinstance(level1_post, list):
        level1_post = [level1_post]
    
    payload_string = json.dumps({
        "Today": today,
        "Level1Post": level1_post
    })
    
    print(f"Payload string being sent: {payload_string}")
    
    response = requests.put(adalo_api_url, headers=headers, data=payload_string)
    
    if response.status_code == 200:
        updated_user_data = response.json()
        print(f"User data updated successfully: {updated_user_data}")
        return updated_user_data  # Return updated user data as JSON
    else:
        print(f"Failed to update user data. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return {"error": "Failed to update user data", "status_code": response.status_code}

# Function to update user's "PracticeBase" field with post IDs
def update_user_practice_base(user_id, practice_base):
    adalo_api_url = f"https://api.adalo.com/v0/apps/23b040ee-e4d1-4873-bb3b-82e902e29e6d/collections/t_9e358c26e7fc41ad814f0a7a2b5d1265/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Ensure practice_base is a list
    if not isinstance(practice_base, list):
        practice_base = [practice_base]
    
    payload_string = json.dumps({
        "PracticeBase": practice_base
    })
    
    print(f"Payload string being sent: {payload_string}")
    
    response = requests.put(adalo_api_url, headers=headers, data=payload_string)
    
    if response.status_code == 200:
        updated_user_data = response.json()
        print(f"User data updated successfully: {updated_user_data}")
        return updated_user_data  # Return updated user data as JSON
    else:
        print(f"Failed to update user data. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return {"error": "Failed to update user data", "status_code": response.status_code}

@app.route('/base-reset', methods=['PATCH'])
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
        subcategory = next((sc for sc in subcategories if str(sc.get('id')) == str(subcategory_id)), None)

        if not subcategory:
            print(f"Error: Subcategory with ID {subcategory_id} not found")
            return jsonify({"error": "Subcategory not found"}), 404

        # Get all posts from the subcategory
        posts_to_add = subcategory.get('Posts', [])
        
        if not posts_to_add:
            print(f"No posts found for subcategory {subcategory_id}")
            return jsonify({"message": "No posts found"}), 200

        # Step 4: Update user's PracticeBase with posts from the specified subcategory
        existing_practice_base = user_data.get('PracticeBase', [])
        updated_practice_base = list(set(existing_practice_base + posts_to_add))

        print(f"Updating user {user_id} PracticeBase with posts from subcategory {subcategory_id}")
        updated_user_data = update_user_practice_base(user_id, updated_practice_base)
        if 'error' in updated_user_data:
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)

        # Return the updated user data
        print(f"User {user_id} updated successfully with posts from subcategory {subcategory_id}")
        return jsonify(updated_user_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['PATCH'])
def test():
    try:
        # Get the user ID and subcategory ID from the request
        user_id = request.json.get('user_id')
        subcategory_id = request.json.get('subcategory_id')
        
        if not user_id or not subcategory_id:
            print("Error: User ID or Subcategory ID not provided")
            return jsonify({"error": "User ID or Subcategory ID not provided"}), 400

        # Step 1: Fetch user data from Adalo API
        print(f"Step 1: Fetching user data for user ID: {user_id}")
        user_data = get_user_data_from_adalo(user_id)
        if 'error' in user_data:
            return jsonify(user_data), user_data.get("status_code", 500)

        # Step 2: Fetch all subcategories
        print(f"Step 2: Fetching subcategories to find subcategory with ID: {subcategory_id}")
        subcategories_data = get_subcategories()
        if 'error' in subcategories_data:
            return jsonify(subcategories_data), subcategories_data.get("status_code", 500)

        # Step 3: Find the specified subcategory and get its posts
        subcategories = subcategories_data.get('records', [])
        subcategory = next((sc for sc in subcategories if str(sc.get('id')) == str(subcategory_id)), None)

        if not subcategory:
            print(f"Error: Subcategory with ID {subcategory_id} not found")
            return jsonify({"error": "Subcategory not found"}), 404

        # Get all posts from the subcategory
        posts_to_add = subcategory.get('Posts', [])
        
        if not posts_to_add:
            print(f"No posts found for subcategory {subcategory_id}")
            return jsonify({"message": "No posts found"}), 200

        # Step 4: Add posts to the "Today" and "Level1Post" fields of the user
        existing_today = user_data.get('Today', [])
        existing_level1_post = user_data.get('Level1Post', [])
        
        updated_today = list(set(existing_today + posts_to_add))
        updated_level1_post = list(set(existing_level1_post + posts_to_add))

        print(f"Updating user {user_id} Today and Level1Post with posts from subcategory {subcategory_id}")
        updated_user_data = update_user_today_and_level1(user_id, updated_today, updated_level1_post)
        if 'error' in updated_user_data:
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)

        # Return the updated user data
        print(f"User {user_id} updated successfully with posts from subcategory {subcategory_id}")
        return jsonify(updated_user_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
