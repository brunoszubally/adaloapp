import requests
import json

# Adalo API key (replace with your actual API key)
ADALO_API_KEY = 'e8wk2i21wge6oxz29ye9u9ykr'

# Function to get all users' data from Adalo
def get_all_users():
    adalo_api_url = "https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_4d891624fa3c4f86b4bce06a08b6ec93"
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

# Function to update user's fields: Today, TodayPlus1, TodayPlus2, TodayPlus3, TodayPlus4, TodayPlus5
def update_user_posts(user_id, today, today_plus_1, today_plus_2, today_plus_3, today_plus_4):
    adalo_api_url = f"https://api.adalo.com/v0/apps/eb904f7c-1bb5-41e8-b35a-5e1453debad3/collections/t_4d891624fa3c4f86b4bce06a08b6ec93/{user_id}"
    headers = {
        'Authorization': f'Bearer {ADALO_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Manually create the JSON payload as a string to match Postman behavior
    payload_string = json.dumps({
        "Today": today,
        "TodayPlus1": today_plus_1,
        "TodayPlus2": today_plus_2,
        "TodayPlus3": today_plus_3,
        "TodayPlus4": today_plus_4,
        "TodayPlus5": []  # Clear TodayPlus5 as it's moved to TodayPlus4
    })
    
    print(f"Updating user {user_id} with new post values")
    
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
            update_user_posts(user_id, updated_today, updated_today_plus_1, updated_today_plus_2, updated_today_plus_3, updated_today_plus_4)
        
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
