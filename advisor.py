"""
advisor.py — core logic for Husky Advisor
Handles searching, filtering, prerequisite checking, and workload estimation.
"""

def get_course_by_id(courses, course_id):
    for c in courses:
        if c["id"] == course_id:
            return c
    return None


def search_courses(courses, query: str):
    """Full-text search across name, description, professor, and career tags."""
    q = query.lower().strip()
    if not q:
        return courses
    results = []
    for c in courses:
        haystack = " ".join([
            c["id"].lower(),
            c["name"].lower(),
            c["description"].lower(),
            c["professor"].lower(),
            " ".join(c["career_tags"]).lower(),
            " ".join(c["tracks"]).lower(),
        ])
        if q in haystack:
            results.append(c)
    return results


def filter_courses(courses, query=None, track=None, difficulty=None, semester=None):
    """Combined filter: text search + track + difficulty + semester."""
    results = courses

    if query and query.strip():
        results = search_courses(results, query)

    if track:
        results = [c for c in results if track in c["tracks"]]

    if difficulty is not None:
        results = [c for c in results if c["difficulty"] == difficulty]

    if semester:
        results = [c for c in results if semester in c["semesters_offered"]]

    return results


def check_prerequisites(courses, course_id: str, completed_ids: list):
    """
    Returns dict: {eligible: bool, missing: [list of missing prereq IDs]}
    """
    course = get_course_by_id(courses, course_id)
    if not course:
        return {"eligible": False, "missing": [], "error": f"Course {course_id} not found"}

    prereqs = course.get("prerequisites", [])
    completed_set = set(completed_ids or [])
    missing = [p for p in prereqs if p not in completed_set]

    return {
        "eligible": len(missing) == 0,
        "missing": missing,
        "course": course,
    }


def get_track_courses(courses, tracks_dict, track_name):
    """Return all course objects for a given concentration track."""
    ids = tracks_dict.get(track_name, [])
    return [c for c in courses if c["id"] in ids]


def workload_check(courses, selected_ids, thresholds):
    """
    Given a list of course IDs, compute total weekly hours and return a status.
    Status: 'safe' | 'caution' | 'heavy' | 'overloaded'
    """
    selected = [c for c in courses if c["id"] in selected_ids]
    total_hours = sum(c["workload_hrs_per_week"] for c in selected)
    total_credits = sum(c["credits"] for c in selected)

    if total_hours <= thresholds["safe_weekly_hours"]:
        status = "safe"
    elif total_hours <= thresholds["caution_weekly_hours"]:
        status = "caution"
    elif total_hours <= thresholds["danger_weekly_hours"]:
        status = "heavy"
    else:
        status = "overloaded"

    return {
        "total_hours": total_hours,
        "total_credits": total_credits,
        "status": status,
        "courses": selected,
    }