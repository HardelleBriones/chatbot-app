import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()
# Use environment variable for the Moodle API token
#MOODLE_API_TOKEN = os.getenv('MOODLE_API_TOKEN')

class MoodleServices:
    def __init__(self, base_url: str = "http://localhost"):
        self.api_token = os.getenv('MOODLE_API_TOKEN')
        self.base_url = f"{base_url}/webservice/rest/server.php"
        
    print("API Token:", os.getenv('MOODLE_API_TOKEN'))

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
    
    # def get_courses_for_user(self, user_id):
    #     """Retrieve courses for a specific user."""
    #     user_courses = self.make_api_call('core_enrol_get_users_courses', {'userid': user_id})
    #     user_info = self.make_api_call('core_user_get_users_by_field', {'field': 'id', 'values[0]': user_id})
    #     user_name = user_info[0]['fullname']
    #     for course in user_courses:
    #         course['contents'] = self.get_course_contents(course['id'])
    #     return {'user_id': user_id, 'user_name': user_name, 'courses': user_courses}
    
    def get_courses_for_user(self, user_id):
        """Retrieve courses for a specific user with detailed content and module information."""
        user_courses = self.make_api_call('core_enrol_get_users_courses', {'userid': user_id})
        courses_data = []

        for course in user_courses:
            course_data = {
                'displayname': course['displayname'],
                'contents': []
            }
            course_contents = self.get_course_contents(course['id'])

            for content in course_contents:
                content_data = {
                    'name': content['name'],
                    'modules': []
                }

                for module in content.get('modules', []):
                    if 'url' in module:
                        module_data = {
                            'url': module['url'],
                            'name': module['name']
                        }
                        content_data['modules'].append(module_data)

                course_data['contents'].append(content_data)

            courses_data.append(course_data)

        return courses_data
        
    

# Example usage:
moodle_service = MoodleServices()
try:
    enrolled_courses = moodle_service.get_courses_for_user(user_id=3)
    #all_courses = moodle_service.get_all_courses()
    print(json.dumps(enrolled_courses, indent=4))
    #print(json.dumps(all_courses, indent=4))
except SystemError as e:
    print(e)