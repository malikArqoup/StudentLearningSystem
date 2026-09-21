import requests
from decouple import config


class OpenEdXClient:
    """
    Thin HTTP client for browsing courses from a public Open edX (edx-platform)
    Courses API - no authentication required for this endpoint.

    Response shape verified directly against https://courses.edx.org (the
    public edX.org LMS instance) as of 2026-09:

    - GET {base}/api/courses/v1/courses/ returns {"results": [...],
      "pagination": {"next", "previous", "count", "num_pages"}}.
    - Each course exposes "id" (course key, "course_id" as a legacy alias),
      "name" (title), "short_description", and a nested "media" object:
      media.image.{raw,small,large} and media.course_image.uri. There is no
      general marketing "course_url" field, so the courseware URL is built
      from the base URL + course id.
    """

    def __init__(self):
        self.base_url = config(
            "OPEN_EDX_BASE_URL",
            default="https://courses.edx.org",
        ).rstrip("/")

    def _headers(self):
        return {
            "Accept": "application/json",
        }

    def _absolute_url(self, url):
        if not url:
            return ""

        if url.startswith("http://") or url.startswith("https://"):
            return url

        return f"{self.base_url}{url}"

    def normalize_course(self, course):
        external_id = (
            course.get("id")
            or course.get("course_id")
        )

        title = course.get("name") or ""

        description = course.get("short_description") or ""

        # The Courses API has no general marketing "course_url" field.
        # Fall back to the standard LMS courseware entry point.
        course_url = course.get("course_url") or (
            f"{self.base_url}/courses/{external_id}/course/"
            if external_id
            else ""
        )

        media = course.get("media") or {}
        image = media.get("image") or {}
        course_image = media.get("course_image") or {}

        image_url = self._absolute_url(
            image.get("raw")
            or image.get("small")
            or image.get("large")
            or course_image.get("uri")
        )

        return {
            "external_id": external_id,
            "provider": "OPEN_EDX",
            "title": title,
            "description": description,
            "course_url": course_url,
            "image_url": image_url,
        }

    def get_courses(self):
        response = requests.get(
            f"{self.base_url}/api/courses/v1/courses/",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        courses = data.get("results", data)

        return [
            self.normalize_course(course)
            for course in courses
        ]


open_edx_client = OpenEdXClient()
