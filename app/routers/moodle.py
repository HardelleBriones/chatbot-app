from fastapi import Depends, status, HTTPException, Response, APIRouter
from services.moodle_services import MoodleServices
from routers.schemas import Course
from typing import List
router = APIRouter(
    prefix="/moodle",
    tags=["moodle"]
)    

moodle_service = MoodleServices()


@router.get("/courses/{user_id}")
def get_courses_for_user(user_id: int):
    """Retrieve courses for a specific user."""
    try:
        courses = moodle_service.get_courses_for_user(user_id)
        if not courses:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No courses found for the user")
        return courses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/courses")
def get_all_courses():
    """Retrieve all courses with their contents."""
    try:
        courses = moodle_service.get_all_courses()
        if not courses:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No courses found")
        return courses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/courses/{course_id}/contents")
def get_course_contents(course_id: int):
    """Retrieve contents for a specific course."""
    try:
        contents = moodle_service.get_course_contents(course_id)
        if not contents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contents found for the course")
        return contents
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/course_name")
def get_course_name(self):
    """Retrieve course name for a specific course."""
    try:
        course_name = moodle_service.get_courses_with_ids(self)
        if not course_name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No course name found")
        return course_name
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))