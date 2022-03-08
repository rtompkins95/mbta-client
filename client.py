"""
Coding challenge for The Broad Institute
Author: Ryan Tompkins
File: A REST client that outputs routes and stops in the Massachusetts Bay Transportation Authority (MBTA)

Libraries:
'requests' - HTTP operations
'argparse' - Parse and validates command line arguments
"""

# READ ME
# make sure to install these packages before running:
# pip install requests
# pip install argparse

# example usage: python3 client.py -routes
#              : python3 client.py -stops RED
#              : python3 client.py
import requests
import argparse

# CONSTANTS
hostname = "https://api-v3.mbta.com"
banner = "\n--------------------------------------------\n"


def get_routes(filter_id):
    """Make a GET call to the /routes endpoint and store the responses in the routes and route_ids dicts

        Args:
            filter_id (str): The filter_id (e.g. Heavy Rail = 0). Default to 'Light Rail' (type 0) and 'Heavy Rail' (type 1)

        Returns:
            routes: A dictionary of route_id -> route (i.e. '/routes' resource JSON response)

    """
    endpoint = "/routes?filter[type]=" + (filter_id if filter_id else "0,1")
    resp = requests.get(_url(endpoint))
    if resp.status_code != 200:
        raise Exception("GET /routes/ {}".format(resp.status_code))

    routes = {}  # route_id -> JSON response for that route
    route_ids = {}  # route_id -> route_id in Pascal case (i.e. RED -> Red) for API endpoint
    for route in resp.json()["data"]:
        route_id = route["id"]
        routes[route_id] = route
        route_ids[route_id] = route_id
    return routes, route_ids


def get_stops(route_id):
    """Get a dictionary of stop_id -> stop (i.e. '/stops?route={route_id}' resource JSON response)

        Args:
            route_id (str): The route_id (i.e. route name) in PascalCase (e.g. 'Green-B')

        Returns:
            stops: A dictionary of stop_id -> stop (the JSON response from '/stops' resource)

    """
    resp = requests.get(_url("/stops?route=" + route_id))
    if resp.status_code != 200:
        # This means something went wrong.
        raise Exception("GET /routes/ {}".format(resp.status_code))

    # later we can cache this from the endpoint to avoid another API call and use id lookup
    # stops[subway_id]
    stops = {}
    for stop in resp.json()["data"]:
        stops[stop["id"]] = stop

    return stops


def _url(path):
    """Given a path representing a REST endpoint/resource, return the hostname + path

        Args:
            path (str): The REST endpoint without a leading forward slash (e.g 'clubs')

         Returns:
            hostname + path: The full path the REST resource

    """
    return hostname + path


def parse_args():
    """Get a dictionary of the command line arguments

        Returns:
            args: A dictionary of CLI name -> flag value (e.g. args['all'] -> True)

    """
    ap = argparse.ArgumentParser()

    ap.add_argument("-s", "-subway", "-stops", "-n", "-name", "-i", "-id", "--id", default="",
                    required=False, help="Print all stops for the given route name")

    ap.add_argument("-f", "-filter", "--filter", default="0,1",
                    required=False, help="'Light Rail' (type 0) and 'Heavy Rail' (type 1)")

    ap.add_argument("-stats", "--stats", action="store_true", default=False,
                    required=False, help="Output stops connecting two or more routes and route with most+least stops")

    ap.add_argument("-path", "--path", default="",
                    required=False, help="<Stop1>-<Stop2>")
    args = vars(ap.parse_args())

    return args


def print_stats(route_ids):
    """Output stops connecting two or more routes and route with most+least stops"

        Args:
            route_ids (dict): route_id -> route_id in Pascal case (i.e. RED -> Red) for API endpoint

    """
    # map every route to a dictionary of all of its stops
    all_stops = {}
    for r in route_ids.keys():
        all_stops[r] = get_stops(r)

    # find the route with the most and least # of stops
    most = (None, -1)
    least = (None, float("inf"))
    for r in route_ids.keys():
        stops = all_stops[r]
        num_stops = len(stops.items())
        if num_stops > most[1]:
            most = (r, num_stops)
        if num_stops < least[1]:
            least = (r, num_stops)
    print("\nRoute with most stops is {} with {} stops".format(most[0], most[1]))
    print("Route with least stops is {} with {} stops".format(least[0], least[1]))

    print("\nStops connecting two or more routes{}".format(banner))

    stops_map = stops_to_routes(route_ids, all_stops)

    for s in stops_map.keys():
        routes = stops_map[s]
        if len(routes) > 1:
            print("{} connects {}".format(s, routes))


def stops_to_routes(route_ids, all_stops):
    """Return a dictionary of stops to their route

        Args:
            route_ids (dict): route_id -> route_id in Pascal case (i.e. RED -> Red) for API endpoint
            all_stops (dict): route_id -> [stops]

         Returns:
            a dictionary of stops to their route

    """
    stops_to_route = {}
    for r in route_ids.keys():
        for stop in all_stops[r].values():
            name = stop["attributes"]["name"]
            if name not in stops_to_route:
                stops_to_route[name] = [r]
            else:
                stops_to_route[name].append(r)
    return stops_to_route


def find_path(stop1, stop2, route_ids):
    """Return the path from route1 to route2

            Args:
                stop1 (str): The starting stop name
                stop2 (str): The destination stop name
                route_ids (dict): route_id -> route_id in Pascal case (i.e. RED -> Red) for API endpoint

             Returns:
                A list of routes needed to get from stop1 to stop2

        """
    # map every route to a dictionary of all of its stops
    all_stops = {}
    for r in route_ids.keys():
        all_stops[r] = get_stops(r)
    stops_map = stops_to_routes(route_ids, all_stops)

    # construct adjacency list graph
    graph = {}
    for s in stops_map.keys():
        routes = stops_map[s]
        for r in routes:
            if r not in graph:
                graph[r] = set({})
            graph[r] = graph[r].union(set(routes))

    for v in graph.keys():
        graph[v] = list(graph[v])

    # BFS search
    start = stops_map[stop1]
    end = stops_map[stop2]

    if start == end:
        return start

    if not start:
        print("Unknown start location: {}".format(start))
    if not end:
        print("Unknown end location: {}".format(end))
    if not start or not end:
        return

    start = start[0]
    end = end[0]

    visited = set({})
    queue = [(graph[start][0], [start])]

    while queue:
        vertex, path = queue.pop()
        if vertex == end:
            return path + [end]
        for neighbor in graph[vertex]:
            if neighbor == end:
                return path + [end]
            else:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
    print("Route not found from {} to {}", stop1, stop2)


def main():
    """Validate CLI arguments and query the MBTA API for routes and/or stops information

    """
    args = parse_args()
    route_id, filter_id, stats, path = args["id"], args["filter"], args["stats"], args["path"]

    # normalize route name
    if route_id:
        route_id = route_id.upper()

    # fetch the list of routes and route_ids
    routes, route_ids = get_routes(filter_id)

    print("All MBTA Routes for types: {}:{}".format(filter_id, banner))
    for key in routes.keys():
        route = routes[key]
        print("ID: {}, NAME: {}".format(key, route["attributes"]["long_name"]))

    # if a route is provided, print all stops for that route
    if route_id:
        if route_id not in route_ids:
            print("Unknown Route NAME: {}{}".format(banner, route_id))
            return
        print("\nAll stops for ROUTE: {}".format(route_id))
        stops = get_stops(route_id)
        for stop_id in stops.keys():
            stop = stops[stop_id]
            data = stop["attributes"]
            print("ID: {}, NAME: {}, ADDRESS: {}".format(stop["id"], data["name"], data["address"]))

    if stats:
        print_stats(route_ids)

    if path:
        stop1, stop2 = path.split("-")
        p = find_path(stop1, stop2, route_ids)
        if p:
            print("{} to {} -> {}".format(stop1, stop2, p))


main()
