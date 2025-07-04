import sys
import requests
from question_filtering import filter_questions
from user_analytics import show_user_analytics

def display_menu():
    """Display the main menu options"""
    print("\n" + "="*50)
    print("    CODEFORCES TUTOR - MAIN MENU")
    print("="*50)
    print("1. Question Filtering")
    print("2. User Analytics")
    print("3. Fetch a New user")
    print("4. Exit")
    print("="*50)

def get_user_input():
    """Get and validate user input"""
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("Invalid choice. Please enter 1, 2, 3 or 4.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

def get_username():
    """Get Codeforces username from user"""
    while True:
        try:
            username = input("\nEnter your Codeforces username: ").strip()
            if username:
                url = f"https://codeforces.com/api/user.info?handles={username}"
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    print("Invalid Username. Please try again...")
                    continue
                return username
            else:
                print("Username cannot be empty. Please try again.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main application function"""
    print("Welcome to Codeforces Tutor!")
    print("A simple tool to help you practice Codeforces problems and analyze your performance.")

    # Get username once at startup
    username = get_username()

    while True:
        display_menu()
        choice = get_user_input()

        if choice == '1':
            print(f"\nStarting Question Filtering for user: {username}")
            filter_questions(username)
        elif choice == '2':
            print(f"\nStarting User Analytics for user: {username}")
            show_user_analytics(username)
        elif choice == '3':
            username = get_username()
        elif choice == '4':
            print("\nThank you for using Codeforces Tutor!")
            print("Happy coding! 🚀")
            break

if __name__ == "__main__":
    main()
