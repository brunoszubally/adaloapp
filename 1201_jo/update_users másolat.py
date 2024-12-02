import requests
import json

# Adalo API key (replace with your actual API key)
ADALO_API_KEY = 'f2oc2cjofs8ctjy8xnpaxjgt7'

# Function to get all users' data from Adalo
def get_all_users():
    adalo_api_url = "https://api.adalo.com/v0/apps/94ea9f02-88f9-4f0b-bba7-93bb710c009a/collections/t_43c2da3e0a4441489c562be24462cb1c"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("Fetching all users from Adalo API")
    response = requests.get(adalo_api_url, headers=headers)
    
    if response.status_code == 200:
        users_data = response.json()
        print(f"Users data retrieved: {users_data}")
        return users_data['records']  # Return all user records as a list
    else:
        print(f"Failed to retrieve users. Status code: {response.status_code}")
        return {"error": "Failed to retrieve users", "status_code": response.status_code}

# Function to update user's Level1PostToUse and Level2PostToUse
def update_user_posts(user_id, level1_posts, level2_posts):
    adalo_api_url = f"https://api.adalo.com/v0/apps/94ea9f02-88f9-4f0b-bba7-93bb710c009a/collections/t_43c2da3e0a4441489c562be24462cb1c/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Manually create the JSON payload as a string to match Postman behavior
    payload_string = json.dumps({
        "Level1PostToUse": level1_posts,
        "Level2PostToUse": level2_posts  # Send an empty array for Level2PostToUse
    })
    
    print(f"Updating user {user_id} with Level1PostToUse: {level1_posts} and clearing Level2PostToUse")
    
    response = requests.put(adalo_api_url, headers=headers, data=payload_string)  # Using 'data' instead of 'json'
    
    if response.status_code == 200:
        updated_user_data = response.json()
        print(f"User {user_id} data updated successfully: {updated_user_data}")
        return updated_user_data  # Return updated user data as JSON
    else:
        print(f"Failed to update user {user_id}. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return {"error": "Failed to update user data", "status_code": response.status_code}

def update_all_users_posts():
    try:
        # Step 1: Fetch all user data from Adalo
        print("Step 1: Fetching all users")
        users = get_all_users()
        if 'error' in users:
            return users
        
        # Step 2: For each user, move posts from Level2PostToUse to Level1PostToUse and empty Level2PostToUse
        for user in users:
            user_id = user['id']
            level1_posts = user.get('Level1PostToUse', [])
            level2_posts = user.get('Level2PostToUse', [])
            
            # Combine Level2PostToUse posts into Level1PostToUse
            updated_level1_posts = level1_posts + level2_posts
            updated_level2_posts = []  # Empty the Level2PostToUse array
            
            # Step 3: Update user posts
            print(f"Updating user {user_id}...")
            update_user_posts(user_id, updated_level1_posts, updated_level2_posts)
        
        # Return success message
        print("All users updated successfully.")
        return {"message": "All users updated successfully"}
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

# Main program entry point
if __name__ == '__main__':
    result = update_all_users_posts()
    print(result)
