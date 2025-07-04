# Codeforces Tutor Web App

A simple web interface for the Codeforces Tutor application.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and go to: http://localhost:5000

## Features

- **Question Filtering**: Filter Codeforces problems by rating, contest type, and other criteria
- **User Analytics**: View detailed statistics about your Codeforces performance
- **Username Management**: Set and change your Codeforces username

## Usage

1. First, set your Codeforces username
2. Use the Question Filtering feature to find problems matching your criteria
3. Use the User Analytics feature to analyze your performance

## Files Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `question_filtering.py` - Question filtering logic (original)
- `user_analytics.py` - User analytics logic (original)
- `main.py` - Original terminal application
