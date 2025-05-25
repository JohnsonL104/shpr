from flask import request

def is_mobile():
    """Check if the current request is from a mobile device based on the User-Agent header."""
    user_agent = request.headers.get('User-Agent').lower()
    mobile_strings = ['android', 'iphone', 'ipad', 'blackberry', 'iemobile', 'opera mini']
    return any(mobile_string in user_agent for mobile_string in mobile_strings)