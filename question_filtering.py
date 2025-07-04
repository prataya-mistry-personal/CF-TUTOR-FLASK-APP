from email.policy import default

import requests
import json
import sys
from typing import List, Dict, Any

def get_user_input_int(prompt: str, min_val: int = 800, max_val: int = 3500, default: int = None) -> int:
    """Get integer input from user with validation"""
    while True:
        try:
            user_input = input(prompt).strip()
            if user_input == "":
                return default
            value = int(user_input)
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            return None

def get_rating_range():
    """Get rating range from user"""
    print("\n--- Rating Range ---")
    print("Enter 800 for no lower bound, 3500 for no upper bound")

    lower_bound = get_user_input_int("Rating range lower bound (type 800 for no lower_bound): ", min_val=800, max_val=3500,default = 800)
    upper_bound = get_user_input_int("Rating range upper bound (type 3500 for no upper_bound): ", min_val=lower_bound, max_val=3500, default = 3500)
    return lower_bound, upper_bound

def get_contest_type() -> List[str]:
    """Get contest type preference from user"""
    print("\n--- Contest Type Preferences ---")
    print("1. Div 1+2")
    print("2. Div 1")
    print("3. Div 2")
    print("4. Div 3")
    print("5. Div 4")
    print("6. No preference")

    # choice = get_user_input_int("Contest type preference (1-6): ", min_val=1, max_val=6, default = 6)
    contest_types = {
        1: "Div. 1 + Div. 2",
        2: "Div. 1",
        3: "Div. 2",
        4: "Div. 3",
        5: "Div. 4",
        6: "no_preference",
    }
    choice = list(map(int, input("Type your contest preferences: ").split()))
    user_choices = ["Div. 1 + Div. 2", "Div. 1", "Div. 2", "Div. 3", "Div. 4"]
    if len(choice) == 0 or len(choice)>=5 or (6 in choice):
        return user_choices

    for i in range(6):
        if i == 0: continue
        if not (i in choice): user_choices.remove(contest_types[i])

    return user_choices

def get_question_range():
    """Get question number preference from user"""
    print("\n--- Question Number Preference ---")
    print("Example: write '2 5' for considering questions 2 to 5 (1-indexed) or write 4 for only question number 4")
    print("Type '0' for no preference")

    while True:
        try:
            user_input = list(map(int, input("Enter list elements: ").split()))
            if len(user_input) == 0 or (len(user_input) == 1 and user_input[0] == 0):
                return 1, 10
            if len(user_input) == 1:
                return user_input[0], user_input[0]

            if len(user_input) == 2:
                if 1 <= user_input[0] <= user_input[1] <= 10:
                    return user_input[0], user_input[1]
                else:
                    print("Question numbers must be between 1-10 and start <= end")
            else:
                print("Please enter two numbers separated by space, or single integer, or '0' for no preference")
        except ValueError:
            print("Please enter valid integers")
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            return None, None

def get_contest_count():
    """Get number of recent contests to consider"""
    print("\n--- Recent Contests ---")
    count = get_user_input_int("Last how many contests to be considered (1-500): ", min_val=1, max_val=500, default=500)
    return count

def get_max_questions():
    """Get maximum number of questions wanted"""
    print("\n--- Maximum Questions ---")
    max_q = get_user_input_int("Maximum number of questions you want (less than 50): ", min_val=1, max_val=50, default=10)
    return max_q

def fetch_contests(user_contest_type:List[str] ,max_contest_count: int = 500):
    """Fetch problems and contests from Codeforces API"""
    try:
        # Fetch contests
        print("Fetching contests from Codeforces API...")
        contests_url = "https://codeforces.com/api/contest.list"
        contests_response = requests.get(contests_url, timeout=10)

        if contests_response.status_code != 200:
            print(f"Error fetching contests: HTTP {contests_response.status_code}")
            return None

        contests_data = contests_response.json()
        if contests_data['status'] != 'OK':
            print(f"Contest API Error: {contests_data.get('comment', 'Unknown error')}")
            return None

        count = 0
        relevant_contests = []
        all_contest_types = ["Div. 1 + Div. 2", "Div. 1", "Div. 2", "Div. 3", "Div. 4"]
        # choose contests according to preference
        for contest in contests_data["result"]:
            if contest["phase"] == "BEFORE": continue
            for this_contest_type in all_contest_types:
                if this_contest_type in contest["name"]:
                    if this_contest_type in user_contest_type:
                        count += 1
                        relevant_contests.append(contest)
                        break
            if count == max_contest_count: break

        return relevant_contests

    except requests.exceptions.Timeout:
        print("Request timeout. Please check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def fetch_problems(contests: List[Dict], filters: Dict)->List[Dict]:
    try:
        print("\nFetching problems from Codeforces API...")

        req_problems = [{}]
        for contest in contests:
            contest_id = contest["id"]
            row1_url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
            row1_response = requests.get(row1_url, timeout=5)

            if row1_response.status_code != 200:
                print(f"Error fetching contests: HTTP {row1_response.status_code}")
                return None

            row1_data = row1_response.json()
            if row1_data['status'] != 'OK':
                print(f"Contest API Error: {row1_data.get('comment', 'Unknown error')}")
                return None
            for i, problem in enumerate(row1_data["result"]["problems"]):
                if (i >= filters["question_start"] - 1) and (i< filters["question_end"]):
                    if ("rating" in problem) and ((problem["rating"]>=filters["rating_lower"]) and problem["rating"]<=filters["rating_upper"]):
                        # print(f"i = {i} rating = {problem["rating"]} id = {contest["id"]}\n")
                        req_problems.append(problem)
                        if len(req_problems)>filters["max_questions"]: break
            if len(req_problems)>filters["max_questions"]: break

        return req_problems[1:]


    except requests.exceptions.Timeout:
        print("Request timeout. Please check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def display_results(problems: List[Dict]):
    """Display filtered problems as links"""
    # print(problems)
    if not problems:
        print("\nNo problems found matching your criteria.")
        return

    print(f"\nFound {len(problems)} problems matching your criteria:")
    print("-" * 60)

    for problem in problems:
        contest_id = problem['contestId']
        index = problem['index']
        link = f"https://codeforces.com/contest/{contest_id}/problem/{index}"
        print(link)

def filter_questions(username: str):
    """Main question filtering function"""
    print(f"\n=== QUESTION FILTERING FOR USER: {username} ===")

    # Get user preferences
    rating_lower, rating_upper = get_rating_range()
    if rating_lower is None or rating_upper is None:
        return

    contest_type = get_contest_type()
    if contest_type is None:
        return

    question_start, question_end = get_question_range()
    if question_start is None and question_end is None:
        return

    contest_count = get_contest_count()
    if contest_count is None:
        return

    max_questions = get_max_questions()
    if max_questions is None:
        return

    # Create filters dictionary
    filters = {
        'rating_lower': rating_lower,
        'rating_upper': rating_upper,
        'contest_type': contest_type,
        'question_start': question_start,
        'question_end': question_end,
        'contest_count': contest_count,
        'max_questions': max_questions
    }

    # Fetch data and filter
    contests_data = fetch_contests(contest_type, contest_count)

    # print(f"size of contests_data = {len(contests_data)}")
    # print(f"contest type = {contest_type}")
    # print(f"question_start = {question_start}")
    # print(f"question_end = {question_end}")
    # print(f"max_questions = {max_questions}")
    # print("contests_data = [")
    # for  c in contests_data:
    #     print(c)
    #     print("\n")
    # print("]\n")

    filtered_problems = fetch_problems(contests_data, filters)

    # Display results
    display_results(filtered_problems)

    print(f"\nFiltering complete!")
    input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    # Test the module
    filter_questions("test_user")
