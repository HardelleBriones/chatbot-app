import requests
import os
import json

# Use environment variable for the Moodle API token

    def make_api_call(self, wsfunction, params=None):
        """General method to make an API call to the Moodle web service."""
        if params is None:
            params = {}
        params['wstoken'] = self.api_token
        params['moodlewsrestformat'] = 'json'
        params['wsfunction'] = wsfunction

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            # You could log the error here and/or re-raise with additional information
            raise SystemError(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            # Handle non-HTTP exceptions here
            raise SystemError(f"Request failed: {e}")

    def get_all_courses(self):
        """Retrieve all courses with their contents."""
        courses = self.make_api_call('core_course_get_courses')
        for course in courses:
            course['contents'] = self.get_course_contents(course['id'])
        return courses

    def get_course_contents(self, course_id):
        """Retrieve contents for a specific course."""
        return self.make_api_call('core_course_get_contents', {'courseid': course_id})
    

# Example usage:
moodle_service = MoodleServices()
try:
except SystemError as e:
    print(e)