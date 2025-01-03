from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Adalo API key (replace with your actual API key)
ADALO_API_KEY = '37pcjgx195y2fxxrww2ijlmzl'

# Function to get user data from Adalo using the provided user_id
def get_user_data_from_adalo(user_id):
    adalo_api_url = f"https://api.adalo.com/v0/apps/48c90838-05d4-4476-afff-25677a38d96d/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
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
    adalo_api_url = "https://api.adalo.com/v0/apps/48c90838-05d4-4476-afff-25677a38d96d/collections/t_64f55035a0aa46bca01afd442a5007be"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(adalo_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return subcategories data as JSON
    else:
        return {"error": "Failed to retrieve subcategories", "status_code": response.status_code}

# Function to update user's fields (csak Today és Level1Post)
def update_user_fields(user_id, today, level1_post):
    adalo_api_url = f"https://api.adalo.com/v0/apps/48c90838-05d4-4476-afff-25677a38d96d/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "Today": today,
        "Level1Post": level1_post
    }
    
    response = requests.put(adalo_api_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to update user data", "status_code": response.status_code}

# Function to get all users' data from Adalo
def get_all_users():
    adalo_api_url = "https://api.adalo.com/v0/apps/48c90838-05d4-4476-afff-25677a38d96d/collections/t_43c2da3e0a4441489c562be24462cb1c"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("Fetching all users from Adalo API")
    response = requests.get(adalo_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()['records']
    else:
        return {"error": "Failed to retrieve users", "status_code": response.status_code}

# Function to update user's Today and TodayPlus fields
def update_user_today_fields(user_id, today_posts, today_plus_1_posts, today_plus_2_posts, today_plus_3_posts, today_plus_4_posts, today_plus_5_posts):
    adalo_api_url = f"https://api.adalo.com/v0/apps/48c90838-05d4-4476-afff-25677a38d96d/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "TodayPosts": today_posts,
        "TodayPlus1Posts": today_plus_1_posts,
        "TodayPlus2Posts": today_plus_2_posts,
        "TodayPlus3Posts": today_plus_3_posts,
        "TodayPlus4Posts": today_plus_4_posts,
        "TodayPlus5Posts": today_plus_5_posts
    }
    
    print(f"Updating user {user_id} with new Today values")
    response = requests.put(adalo_api_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json()
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

        # Step 4: Update user's Today and Level1Post fields (PracticeBase removed)
        existing_today = user_data.get('Today', [])
        existing_level1_post = user_data.get('Level1Post', [])

        updated_today = list(set(existing_today + posts_to_add))
        updated_level1_post = list(set(existing_level1_post + posts_to_add))

        updated_user_data = update_user_fields(user_id, updated_today, updated_level1_post)
        if 'error' in updated_user_data:
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)

        return jsonify(updated_user_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-all-users', methods=['POST'])
def update_all_users_endpoint():
    try:
        print("Starting update process for all users")
        # Step 1: Fetch all users
        users = get_all_users()
        if 'error' in users:
            return jsonify(users), users.get("status_code", 500)
        
        results = []
        # Step 2: Update each user's Today fields
        for user in users:
            user_id = user['id']
            today_posts = user.get('TodayPosts', [])
            today_plus_1_posts = user.get('TodayPlus1Posts', [])
            today_plus_2_posts = user.get('TodayPlus2Posts', [])
            today_plus_3_posts = user.get('TodayPlus3Posts', [])
            today_plus_4_posts = user.get('TodayPlus4Posts', [])
            today_plus_5_posts = user.get('TodayPlus5Posts', [])
            
            # Move posts down the chain
            updated_today_posts = today_posts + today_plus_1_posts
            updated_today_plus_1_posts = today_plus_2_posts
            updated_today_plus_2_posts = today_plus_3_posts
            updated_today_plus_3_posts = today_plus_4_posts
            updated_today_plus_4_posts = today_plus_5_posts
            updated_today_plus_5_posts = []  # Empty array for TodayPlus5Posts
            
            print(f"Updating user {user_id}...")
            result = update_user_today_fields(
                user_id, 
                updated_today_posts,
                updated_today_plus_1_posts,
                updated_today_plus_2_posts,
                updated_today_plus_3_posts,
                updated_today_plus_4_posts,
                updated_today_plus_5_posts
            )
            results.append({"user_id": user_id, "result": result})
        
        print("All users updated successfully")
        return jsonify({"message": "All users updated successfully", "results": results})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
