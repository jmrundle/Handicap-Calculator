import math                 # distance functions
import database as db


def get_current_pos():
    pos = None

    try:
        from geocoder import ip
        pos = ip("me").latlng

    except Exception as e:
        print("Error: " + str(e))

    return pos


def between(p1, p2):
    """Returns Euclidean distance in miles between two lat-long values"""
    # https://www.movable-type.co.uk/scripts/latlong.html
    if not isinstance(p1, (list, tuple)) or \
        not isinstance(p2, (list, tuple)) or \
        len(p1) < 2 or len(p2) < 2 or \
        not all(tuple(map(lambda num: isinstance(num, (int, float)), p1))) or \
        not all(tuple(map(lambda num: isinstance(num, (int, float)), p2))):

        return -1

    radius = 3959.0  # miles
    lat1 = math.radians(p1[0])
    lat2 = math.radians(p2[0])
    dx = math.radians(p2[0] - p1[0])
    dy = math.radians(p2[1] - p1[1])

    a = math.sin(dx/2) * math.sin(dx/2) + \
        math.cos(lat1) * math.cos(lat2) * \
        math.sin(dy/2) * math.sin(dy/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return round(radius * c, 1)


def to(p2):
    return between(get_current_pos(), p2)


def courses_within(max_dist, limit=20, from_pos=None):
    """Returns list of courses within a certain distance"""
    # if not given an initial position, set initial position to current location
    if from_pos is None:
        current_pos = get_current_pos()

        # if geo-coder failed to get current pos
        if current_pos is None:
            return []
        else:
            from_pos = current_pos
    
    ids = []
    for course in db.courses.get_all("SELECT CourseID, Latitude, Longitude FROM CourseData"):
        try:
            to_pos = (float(course.latitude), float(course.longitude))
            distance = between(from_pos, to_pos)
            if distance <= max_dist:
                ids.append((course.id, distance))
        except ValueError:
            # for courses without a lat-long value ("N/A")
            pass

    # sort results by distance, and cut off by limit
    return sorted(ids, key=lambda x: x[1])[:limit]


if __name__ == '__main__':
    position = get_current_pos()

    print(position)
    print(to([10.3, 20.3]))
    print(courses_within(20))
