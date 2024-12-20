from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Adalo API key (replace with your actual API key)
ADALO_API_KEY = '3vwy1xwqgne181wolentnfy56'

# Function to get user data from Adalo using the provided user_id
def get_user_data_from_adalo(user_id):
    adalo_api_url = f"https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
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
    adalo_api_url = "https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_64f55035a0aa46bca01afd442a5007be"
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
    adalo_api_url = f"https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
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

# Function to update user's fields: Today, TodayPlus1, TodayPlus2, TodayPlus3, TodayPlus4, TodayPlus5
def update_user_posts(user_id, today, today_plus_1, today_plus_2, today_plus_3, today_plus_4):
    adalo_api_url = f"https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload_string = json.dumps({
        "Today": today,
        "TodayPlus1": today_plus_1,
        "TodayPlus2": today_plus_2,
        "TodayPlus3": today_plus_3,
        "TodayPlus4": today_plus_4,
        "TodayPlus5": []
    })
    
    print(f"Updating user {user_id} with new post values")
    response = requests.put(adalo_api_url, headers=headers, data=payload_string)
    
    if response.status_code == 200:
        updated_user_data = response.json()
        print(f"User {user_id} data updated successfully: {updated_user_data}")
        return updated_user_data
    else:
        print(f"Failed to update user {user_id}. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return {"error": "Failed to update user data", "status_code": response.status_code}

def update_user_levels_and_posts(user_id, current_post, updated_fields):
    adalo_api_url = f"https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Hozzáadjuk a showanswertest mezőt is
    updated_fields['showanswertest'] = 0
    
    response = requests.put(adalo_api_url, headers=headers, data=json.dumps(updated_fields))
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to update user data", "status_code": response.status_code}

def get_all_users():
    adalo_api_url = "https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_43c2da3e0a4441489c562be24462cb1c"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(adalo_api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('records', [])
    else:
        return {"error": "Failed to retrieve users", "status_code": response.status_code}

@app.route('/start', methods=['PATCH'])
def combined_reset():
    try:
        # Get the user ID and subcategory ID from the request
        user_id = request.json.get('user_id')
        subcategory_id = request.json.get('subcategory_id')
        
        print(f"Starting reset process for user_id: {user_id}, subcategory_id: {subcategory_id}")
        
        if not user_id or not subcategory_id:
            print("Error: Missing user_id or subcategory_id in request")
            return jsonify({"error": "User ID or Subcategory ID not provided"}), 400

        # Step 1: Fetch user data from Adalo API
        print(f"Step 1: Fetching user data for user_id: {user_id}")
        user_data = get_user_data_from_adalo(user_id)
        if 'error' in user_data:
            print(f"Error fetching user data: {user_data}")
            return jsonify(user_data), user_data.get("status_code", 500)
        print(f"User data retrieved: {user_data}")

        # Step 2: Fetch all subcategories
        print("Step 2: Fetching all subcategories")
        subcategories_data = get_subcategories()
        if 'error' in subcategories_data:
            print(f"Error fetching subcategories: {subcategories_data}")
            return jsonify(subcategories_data), subcategories_data.get("status_code", 500)
        print(f"Subcategories data retrieved successfully")

        # Step 3: Find the specified subcategory and get its posts
        print(f"Step 3: Finding subcategory {subcategory_id}")
        subcategories = subcategories_data.get('records', [])
        subcategory = next((sc for sc in subcategories if str(sc.get('id')) == str(subcategory_id)), None)

        if not subcategory:
            print(f"Error: Subcategory {subcategory_id} not found")
            return jsonify({"error": "Subcategory not found"}), 404

        # Get all posts from the subcategory
        posts_to_add = subcategory.get('Posts', [])
        print(f"Found {len(posts_to_add)} posts in subcategory")
        
        if not posts_to_add:
            print("Warning: No posts found in subcategory")
            return jsonify({"message": "No posts found"}), 200

        # Step 4: Update user's fields
        print("Step 4: Updating user fields")
        existing_practice_base = user_data.get('PracticeBase', [])
        existing_today = user_data.get('Today', [])
        existing_level1_post = user_data.get('Level1Post', [])

        updated_practice_base = list(set(existing_practice_base + posts_to_add))
        updated_today = list(set(existing_today + posts_to_add))
        updated_level1_post = list(set(existing_level1_post + posts_to_add))

        print(f"Updating user fields with:")
        print(f"- PracticeBase: {len(updated_practice_base)} posts")
        print(f"- Today: {len(updated_today)} posts")
        print(f"- Level1Post: {len(updated_level1_post)} posts")

        updated_user_data = update_user_fields(user_id, updated_today, updated_level1_post, updated_practice_base)
        if 'error' in updated_user_data:
            print(f"Error updating user fields: {updated_user_data}")
            return jsonify(updated_user_data), updated_user_data.get("status_code", 500)

        print("Successfully updated all user fields")
        return jsonify(updated_user_data)

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/update-all-users', methods=['POST'])
def update_all_users_endpoint():
    try:
        # Step 1: Fetch all user data from Adalo
        print("Step 1: Fetching all users")
        users = get_all_users()
        if 'error' in users:
            return jsonify(users), users.get("status_code", 500)
        
        results = []
        # Step 2: For each user, move posts from each list to the next one down
        for user in users:
            user_id = user['id']
            today = user.get('Today', [])
            today_plus_1 = user.get('TodayPlus1', [])
            today_plus_2 = user.get('TodayPlus2', [])
            today_plus_3 = user.get('TodayPlus3', [])
            today_plus_4 = user.get('TodayPlus4', [])
            today_plus_5 = user.get('TodayPlus5', [])
            
            # Move the posts from each list to the next list down
            updated_today = today + today_plus_1
            updated_today_plus_1 = today_plus_2
            updated_today_plus_2 = today_plus_3
            updated_today_plus_3 = today_plus_4
            updated_today_plus_4 = today_plus_5
            
            # Step 3: Update user posts
            print(f"Updating user {user_id}...")
            result = update_user_posts(
                user_id, 
                updated_today, 
                updated_today_plus_1, 
                updated_today_plus_2, 
                updated_today_plus_3, 
                updated_today_plus_4
            )
            results.append({"user_id": user_id, "result": result})
        
        print("All users updated successfully.")
        return jsonify({"message": "All users updated successfully", "results": results})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/move-current-post', methods=['PATCH'])
def move_current_post():
    try:
        user_id = request.json.get('user_id')
        current_post = int(request.json.get('current_post'))
        
        # Előre definiáljuk a szint-párosításokat
        level_mappings = {
            'Level1Post': ('Level2Post', 'TodayPlus3'),
            'Level2Post': ('Level3Post', 'TodayPlus4'),
            'Level3Post': ('Level4Post', 'TodayPlus5'),
            'Level4Post': ('CompletedPost', None)
        }
        
        # Csak a szükséges mezőket kérjük le
        response = requests.get(
            f"https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}",
            headers={'Authorization': f'Bearer {ADALO_API_KEY}', 'Content-Type': 'application/json'},
            params={'fields': 'Today,Level1Post,Level2Post,Level3Post,Level4Post,CompletedPost,TodayPlus3,TodayPlus4,TodayPlus5'}
        )
        user_data = response.json()
        
        # Inicializáljuk az updated_fields-et csak a Today listával
        updated_fields = {
            'Today': [post for post in user_data.get('Today', []) if post != current_post]
        }
        
        # Gyors keresés a megfelelő szinten
        for current_level, (next_level, today_plus) in level_mappings.items():
            if current_post in user_data.get(current_level, []):
                # Kivesszük a current_post-ot a jelenlegi szintből
                updated_fields[current_level] = [
                    post for post in user_data[current_level] if post != current_post
                ]
                # Hozzáadjuk a következő szinthez
                updated_fields[next_level] = user_data.get(next_level, []) + [current_post]
                # Ha van TodayPlus mező, azt is frissítjük
                if today_plus:
                    updated_fields[today_plus] = user_data.get(today_plus, []) + [current_post]
                break  # Kilépünk, mert megtaláltuk a megfelelő szintet
        
        # Csak ha van változás, akkor küldjük
        if updated_fields:
            updated_fields['showanswertest'] = 0
            response = requests.put(
                f"https://api.adalo.com/v0/apps/1f62c648-0b5e-4453-9db7-eeb15c043ed2/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}",
                headers={'Authorization': f'Bearer {ADALO_API_KEY}', 'Content-Type': 'application/json'},
                json=updated_fields
            )
            return jsonify(response.json())
        
        return jsonify({"message": "No changes needed"})
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
