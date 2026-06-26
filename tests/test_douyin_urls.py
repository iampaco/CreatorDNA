import re

VIDEO_PATH = re.compile(r"/video/(\d+)")
USER_PATH = re.compile(r"/user/([^/?#]+)")


def detect_page_type(url: str) -> str:
    if VIDEO_PATH.search(url):
        return "video"
    if USER_PATH.search(url):
        return "creator"
    return "unknown"


def extract_video_id(url: str) -> str | None:
    match = VIDEO_PATH.search(url)
    return match.group(1) if match else None
