import json
import os
import datetime
from collections import Counter, defaultdict

MEMORY_FILE = "long_term_memory.json"

def load_history():
    """Loads the long-term memory file."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
        return data.get("activity_log", [])
    except:
        return []

def analyze_habits():
    """
    Analyzes history to find patterns.
    Returns a dictionary: { "Hour (0-23)": "Most Frequent Activity" }
    Example: { "22": "Visual Studio Code" }
    """
    logs = load_history()
    if not logs: return {}
    
    # Structure: hour_map[hour] = Counter(activities)
    hour_map = defaultdict(Counter)
    
    for entry in logs:
        # Expected format: "[YYYY-MM-DD HH:MM:SS] User is using: Activity Name"
        try:
            timestamp_str = entry.split("]")[0].strip("[")
            activity = entry.split("User is using:")[1].strip()
            
            dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            hour_str = str(dt.hour)
            
            # Simple cleaning: Remove specific window titles, keep app name if possible
            # Heuristic: Take the last part of " - " if available, often the App Name
            # e.g. "main.py - Visual Studio Code" -> "Visual Studio Code"
            if " - " in activity:
                app_name = activity.split(" - ")[-1]
            else:
                app_name = activity
                
            hour_map[hour_str][app_name] += 1
            
        except Exception as e:
            continue
            
    # Determine dominant habit for each hour
    habits = {}
    for hour, counts in hour_map.items():
        # Get the most common activity
        top_activity, count = counts.most_common(1)[0]
        # Threshold: Must have done it at least 3 times to be a "habit"
        if count >= 3:
            habits[hour] = top_activity
            
    return habits

def get_proactive_suggestion(current_context=""):
    """
    Checks if the user should be doing something else based on habits.
    Returns a string (suggestion) or None.
    """
    habits = analyze_habits()
    if not habits: return None
    
    now = datetime.datetime.now()
    current_hour = str(now.hour)
    
    if current_hour in habits:
        usual_activity = habits[current_hour]
        
        # If user is ALREADY doing it, no need to suggest
        # Fuzzy matching
        if usual_activity.lower() in current_context.lower():
            return None
            
        return f"Usually you are using {usual_activity} around this time. Want to switch?"
        
    return None
