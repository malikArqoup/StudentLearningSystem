import base64

import requests
from decouple import config


class OpenEdXClient:
    """
    Thin HTTP client for a single Open edX (edx-platform) LMS instance.

    Deployment-specific assumptions are documented here rather than left
    implicit, per the current edx-platform documentation/source
    (docs.openedx.org and github.com/openedx/edx-platform):

    - Token endpoint: POST {base}/oauth2/access_token using HTTP Basic Auth
      (base64 "client_id:client_secret") plus grant_type=client_credentials
      and token_type=jwt in the body. Subsequent API calls authenticate with
      "Authorization: JWT <access_token>".
    - Courses list: GET {base}/api/courses/v1/courses/. Each course exposes
      "id" (course key), "name" (title), "short_description", and a nested
      "media": {"course_image": {"uri": ...}} - there is no flat top-level
      "course_image" field and no general marketing "course_url" field in
      this API, so the courseware URL is built from the base URL + course id.
    - Enrollment: POST {base}/api/enrollment/v1/enrollment. Open edX resolves
      the "user" field as an LMS *username* (User.objects.get(username=...)),
      not an email address. Our local User model authenticates by email only
      and has no separate username, so this client assumes the target Open
      edX deployment provisions usernames equal to the student's email
      (true for many SSO/email-provisioned deployments). A deployment that
      uses distinct usernames would need a real email -> username mapping
      (e.g. via Open edX's Third Party Auth ID Mapping API) before calling
      this client - that mapping is out of scope for this task.
    """

    def __init__(self):
        self.base_url = config("OPEN_EDX_BASE_URL").rstrip("/")
        self.client_id = config("OPEN_EDX_CLIENT_ID")
        self.client_secret = config("OPEN_EDX_CLIENT_SECRET")

    def _get_access_token(self):
        credentials = f"{self.client_id}:{self.client_secret}"

        encoded_credentials = base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")

        response = requests.post(
            f"{self.base_url}/oauth2/access_token",
            headers={
                "Authorization": f"Basic {encoded_credentials}",
                "Cache-Control": "no-cache",
            },
            data={
                "grant_type": "client_credentials",
                "token_type": "jwt",
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()["access_token"]

    def _headers(self):
        return {
            "Authorization": f"JWT {self._get_access_token()}",
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

        title = (
            course.get("name")
            or course.get("display_name")
            or ""
        )

        description = (
            course.get("short_description")
            or course.get("description")
            or ""
        )

        # The Courses API has no general marketing "course_url" field.
        # Fall back to the standard LMS courseware entry point.
        course_url = course.get("course_url") or (
            f"{self.base_url}/courses/{external_id}/course/"
            if external_id
            else ""
        )

        media = course.get("media") or {}
        course_image = media.get("course_image") or {}

        image_url = self._absolute_url(
            course_image.get("uri")
            or course.get("course_image")
            or course.get("image_url")
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

    def enroll_student(self, course_id, student_email):
        response = requests.post(
            f"{self.base_url}/api/enrollment/v1/enrollment",
            headers={
                **self._headers(),
                "Content-Type": "application/json",
            },
            json={
                "course_details": {
                    "course_id": course_id,
                },
                # See the class docstring: Open edX expects an LMS username
                # here. We assume username == email for this deployment.
                "user": student_email,
                "is_active": True,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()


open_edx_client = OpenEdXClient()
