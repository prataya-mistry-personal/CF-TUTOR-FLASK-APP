#!/usr/bin/env python3

"""
Codeforces Tutor - Web Application
Simple Flask-based web interface for the Codeforces tutor
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sys
import os
from datetime import datetime
from question_filtering import fetch_contests, fetch_problems, display_results
from user_analytics import (
    fetch_user_info, fetch_user_submissions, fetch_user_rating_history,
    analyze_submissions, display_user_info, display_submission_stats
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Custom template filter for timestamp conversion
@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """Convert timestamp to readable date format"""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%m-%d %H:%M')
    return 'N/A'

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/set_username', methods=['GET', 'POST'])
def set_username():
    """Set or change username"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            # Simple validation - you can add more validation here
            session['username'] = username
            flash(f'Username set to: {username}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please enter a valid username', 'error')

    return render_template('set_username.html')

@app.route('/question_filtering', methods=['GET', 'POST'])
def question_filtering():
    """Question filtering page"""
    if 'username' not in session:
        flash('Please set your username first', 'error')
        return redirect(url_for('set_username'))

    if request.method == 'POST':
        try:
            # Get form data
            rating_lower = int(request.form.get('rating_lower', 800))
            rating_upper = int(request.form.get('rating_upper', 3500))

            # Contest types
            contest_types = request.form.getlist('contest_types')
            if not contest_types:
                contest_types = ["Div. 1 + Div. 2", "Div. 1", "Div. 2", "Div. 3", "Div. 4"]

            question_start = int(request.form.get('question_start', 1))
            question_end = int(request.form.get('question_end', 10))
            contest_count = int(request.form.get('contest_count', 50))
            max_questions = int(request.form.get('max_questions', 10))

            # Create filters dictionary
            filters = {
                'rating_lower': rating_lower,
                'rating_upper': rating_upper,
                'contest_type': contest_types,
                'question_start': question_start,
                'question_end': question_end,
                'contest_count': contest_count,
                'max_questions': max_questions
            }

            # Fetch and filter problems
            contests_data = fetch_contests(contest_types, contest_count)
            if contests_data:
                problems = fetch_problems(contests_data, filters)
                return render_template('question_results.html',
                                     problems=problems,
                                     filters=filters,
                                     username=session['username'])
            else:
                flash('No contests found matching your criteria', 'error')

        except Exception as e:
            flash(f'Error processing request: {str(e)}', 'error')

    return render_template('question_filtering.html', username=session.get('username'))

@app.route('/user_analytics')
def user_analytics():
    """User analytics page"""
    if 'username' not in session:
        flash('Please set your username first', 'error')
        return redirect(url_for('set_username'))

    username = session['username']

    try:
        # Fetch user information
        user_info, error = fetch_user_info(username)
        if error:
            flash(f'Error fetching user info: {error}', 'error')
            return redirect(url_for('index'))

        # Fetch submissions
        submissions, error = fetch_user_submissions(username, 1000)
        if error:
            flash(f'Error fetching submissions: {error}', 'error')
            return redirect(url_for('index'))

        # Analyze submissions
        stats = analyze_submissions(submissions) if submissions else {}

        # Fetch rating history
        rating_history, _ = fetch_user_rating_history(username)

        return render_template('user_analytics.html',
                             user_info=user_info,
                             stats=stats,
                             rating_history=rating_history,
                             username=username)

    except Exception as e:
        flash(f'Error processing analytics: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='127.0.0.1', port=80)
