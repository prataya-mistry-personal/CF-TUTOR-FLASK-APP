import requests
import json
from collections import defaultdict, Counter
from datetime import datetime
import sys

def fetch_user_info(username: str):
    """Fetch user basic information"""
    try:
        url = f"https://codeforces.com/api/user.info?handles={username}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None, f"HTTP Error {response.status_code}"

        data = response.json()
        if data['status'] != 'OK':
            return None, data.get('comment', 'Unknown API error')

        if not data['result']:
            return None, "User not found"

        return data['result'][0], None

    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def fetch_user_submissions(username: str, count: int = 1000):
    """Fetch user submissions"""
    try:
        print(f"Fetching submissions for {username}...")
        url = f"https://codeforces.com/api/user.status?handle={username}&from=1&count={count}"
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            return None, f"HTTP Error {response.status_code}"

        data = response.json()
        if data['status'] != 'OK':
            return None, data.get('comment', 'Unknown API error')

        return data['result'], None

    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def fetch_user_rating_history(username: str):
    """Fetch user rating history"""
    try:
        url = f"https://codeforces.com/api/user.rating?handle={username}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None, f"HTTP Error {response.status_code}"

        data = response.json()
        if data['status'] != 'OK':
            return None, data.get('comment', 'Unknown API error')

        return data['result'], None

    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def analyze_submissions(submissions):
    """Analyze user submissions for various statistics"""
    if not submissions:
        return {}

    stats = {
        'total_submissions': len(submissions),
        'accepted_submissions': 0,
        'wrong_answer': 0,
        'time_limit_exceeded': 0,
        'runtime_error': 0,
        'compilation_error': 0,
        'other_verdicts': 0,
        'solved_problems': set(),
        'attempted_problems': set(),
        'languages': Counter(),
        'tags': Counter(),
        'rating_distribution': Counter(),
        'contest_participation': set(),
        'recent_activity': []
    }

    for submission in submissions:
        verdict = submission.get('verdict', 'UNKNOWN')

        # Count verdicts
        if verdict == 'OK':
            stats['accepted_submissions'] += 1
            # Add solved problem
            problem = submission.get('problem', {})
            if 'contestId' in problem and 'index' in problem:
                stats['solved_problems'].add((problem['contestId'], problem['index']))
        elif verdict == 'WRONG_ANSWER':
            stats['wrong_answer'] += 1
        elif verdict == 'TIME_LIMIT_EXCEEDED':
            stats['time_limit_exceeded'] += 1
        elif verdict == 'RUNTIME_ERROR':
            stats['runtime_error'] += 1
        elif verdict == 'COMPILATION_ERROR':
            stats['compilation_error'] += 1
        else:
            stats['other_verdicts'] += 1

        # Add attempted problem
        problem = submission.get('problem', {})
        if 'contestId' in problem and 'index' in problem:
            stats['attempted_problems'].add((problem['contestId'], problem['index']))

        # Count programming languages
        lang = submission.get('programmingLanguage', 'Unknown')
        stats['languages'][lang] += 1

        # Count problem tags (only for solved problems)
        if verdict == 'OK' and problem:
            tags = problem.get('tags', [])
            for tag in tags:
                stats['tags'][tag] += 1

            # Count rating distribution
            if 'rating' in problem:
                rating_range = (problem['rating'] // 100) * 100
                stats['rating_distribution'][rating_range] += 1

        # Track contest participation
        if submission.get('contestId'):
            stats['contest_participation'].add(submission['contestId'])

        # Recent activity (last 10 submissions)
        if len(stats['recent_activity']) < 10:
            stats['recent_activity'].append({
                'problem_name': problem.get('name', 'Unknown'),
                'verdict': verdict,
                'contest_id': submission.get('contestId'),
                'index': problem.get('index'),
                'timestamp': submission.get('creationTimeSeconds')
            })

    stats['unique_problems_solved'] = len(stats['solved_problems'])
    stats['unique_problems_attempted'] = len(stats['attempted_problems'])
    stats['unsolved_attempts'] = stats['total_submissions'] - stats['accepted_submissions']

    return stats

def display_user_info(user_info):
    """Display user basic information"""
    print("\n" + "="*60)
    print("                    USER INFORMATION")
    print("="*60)

    print(f"Handle: {user_info.get('handle', 'N/A')}")

    if 'firstName' in user_info and 'lastName' in user_info:
        print(f"Name: {user_info['firstName']} {user_info['lastName']}")

    if 'country' in user_info:
        print(f"Country: {user_info['country']}")

    if 'organization' in user_info:
        print(f"Organization: {user_info['organization']}")

    print(f"Current Rating: {user_info.get('rating', 'Unrated')}")
    print(f"Max Rating: {user_info.get('maxRating', 'N/A')}")
    print(f"Rank: {user_info.get('rank', 'N/A')}")
    print(f"Max Rank: {user_info.get('maxRank', 'N/A')}")
    print(f"Contribution: {user_info.get('contribution', 0)}")
    print(f"Friends: {user_info.get('friendOfCount', 0)}")

    # Registration date
    if 'registrationTimeSeconds' in user_info:
        reg_date = datetime.fromtimestamp(user_info['registrationTimeSeconds'])
        print(f"Registered: {reg_date.strftime('%Y-%m-%d')}")

    # Last online
    if 'lastOnlineTimeSeconds' in user_info:
        last_online = datetime.fromtimestamp(user_info['lastOnlineTimeSeconds'])
        print(f"Last Online: {last_online.strftime('%Y-%m-%d %H:%M')}")

def display_submission_stats(stats):
    """Display submission statistics"""
    print("\n" + "="*60)
    print("                 SUBMISSION STATISTICS")
    print("="*60)

    print(f"Total Submissions: {stats['total_submissions']}")
    print(f"Accepted Submissions: {stats['accepted_submissions']}")
    print(f"Unsolved Attempts: {stats['unsolved_attempts']}")

    if stats['total_submissions'] > 0:
        acceptance_rate = (stats['accepted_submissions'] / stats['total_submissions']) * 100
        print(f"Acceptance Rate: {acceptance_rate:.1f}%")

    print(f"\nUnique Problems Attempted: {stats['unique_problems_attempted']}")
    print(f"Unique Problems Solved: {stats['unique_problems_solved']}")

    # Verdict breakdown
    print("\n--- Verdict Breakdown ---")
    print(f"✅ Accepted: {stats['accepted_submissions']}")
    print(f"❌ Wrong Answer: {stats['wrong_answer']}")
    print(f"⏰ Time Limit Exceeded: {stats['time_limit_exceeded']}")
    print(f"💥 Runtime Error: {stats['runtime_error']}")
    print(f"🔧 Compilation Error: {stats['compilation_error']}")
    print(f"❓ Other Verdicts: {stats['other_verdicts']}")

def display_language_stats(stats):
    """Display programming language statistics"""
    if not stats['languages']:
        return

    print("\n" + "="*60)
    print("              PROGRAMMING LANGUAGES USED")
    print("="*60)

    for lang, count in stats['languages'].most_common(10):
        percentage = (count / stats['total_submissions']) * 100
        print(f"{lang}: {count} submissions ({percentage:.1f}%)")

def display_tag_distribution(stats):
    """Display problem tags distribution for solved problems"""
    if not stats['tags']:
        print("\n--- Problem Tags Distribution ---")
        print("No solved problems with tags found.")
        return

    print("\n" + "="*60)
    print("           SOLVED PROBLEMS BY TAG")
    print("="*60)

    print("Top problem categories you've solved:")
    for tag, count in stats['tags'].most_common(15):
        print(f"{tag}: {count} problems")

def display_rating_distribution(stats):
    """Display rating distribution of solved problems"""
    if not stats['rating_distribution']:
        print("\n--- Rating Distribution ---")
        print("No solved problems with ratings found.")
        return

    print("\n" + "="*60)
    print("        SOLVED PROBLEMS BY DIFFICULTY")
    print("="*60)

    for rating, count in sorted(stats['rating_distribution'].items()):
        print(f"{rating} rated: {count} problems")

def display_recent_activity(stats):
    """Display recent submission activity"""
    if not stats['recent_activity']:
        return

    print("\n" + "="*60)
    print("                RECENT ACTIVITY")
    print("="*60)

    print("Last 10 submissions:")
    for i, activity in enumerate(stats['recent_activity'], 1):
        verdict_emoji = "✅" if activity['verdict'] == 'OK' else "❌"
        problem_id = f"{activity['contest_id']}{activity['index']}" if activity['contest_id'] and activity['index'] else "N/A"

        timestamp_str = ""
        if activity['timestamp']:
            timestamp = datetime.fromtimestamp(activity['timestamp'])
            timestamp_str = timestamp.strftime('%m-%d %H:%M')

        print(f"{i:2d}. {verdict_emoji} {activity['problem_name'][:40]} ({problem_id}) [{timestamp_str}]")

def display_contest_performance(rating_history):
    """Display contest performance"""
    if not rating_history:
        print("\n--- Contest Performance ---")
        print("No contest participation found.")
        return

    print("\n" + "="*60)
    print("              CONTEST PERFORMANCE")
    print("="*60)

    print(f"Total Rated Contests: {len(rating_history)}")

    if len(rating_history) >= 2:
        recent_contests = rating_history[-5:]  # Last 5 contests
        print("\nRecent Contest Performance:")

        for contest in recent_contests:
            contest_name = contest.get('contestName', 'Unknown Contest')
            old_rating = contest.get('oldRating', 0)
            new_rating = contest.get('newRating', 0)
            change = new_rating - old_rating
            change_str = f"+{change}" if change >= 0 else str(change)

            print(f"{contest_name[:50]}: {old_rating} → {new_rating} ({change_str})")

        # Rating change statistics
        changes = [c.get('newRating', 0) - c.get('oldRating', 0) for c in rating_history]
        positive_changes = len([c for c in changes if c > 0])
        negative_changes = len([c for c in changes if c < 0])

        print(f"\nRating Change Summary:")
        print(f"Positive changes: {positive_changes}")
        print(f"Negative changes: {negative_changes}")
        print(f"No change: {len(changes) - positive_changes - negative_changes}")

def show_user_analytics(username: str):
    """Main user analytics function"""
    print(f"\n=== USER ANALYTICS FOR: {username} ===")

    # Fetch user information
    print("Fetching user information...")
    user_info, error = fetch_user_info(username)
    if error:
        print(f"Error fetching user info: {error}")
        print("Please check if the username is correct and try again.")
        input("\nPress Enter to return to main menu...")
        return

    # Display user information
    display_user_info(user_info)

    # Fetch submissions
    submissions, error = fetch_user_submissions(username, 1000)
    if error:
        print(f"\nError fetching submissions: {error}")
        input("\nPress Enter to return to main menu...")
        return

    if not submissions:
        print("\nNo submissions found for this user.")
        input("\nPress Enter to return to main menu...")
        return

    # Analyze submissions
    print("\nAnalyzing submissions...")
    stats = analyze_submissions(submissions)

    # Display all statistics
    display_submission_stats(stats)
    display_language_stats(stats)
    display_tag_distribution(stats)
    display_rating_distribution(stats)
    display_recent_activity(stats)

    # Fetch and display contest performance
    print("\nFetching contest performance...")
    rating_history, error = fetch_user_rating_history(username)
    if not error:
        display_contest_performance(rating_history)
    else:
        print(f"Could not fetch rating history: {error}")

    print("\n" + "="*60)
    print("                 ANALYSIS COMPLETE")
    print("="*60)

    input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    # Test the module
    show_user_analytics("mistryman")
