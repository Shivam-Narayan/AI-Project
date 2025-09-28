import math
import pandas as pd
import streamlit as st

# Define your functions
def haversine_distance(point1, point2):
    # Haversine formula to calculate the distance between two latitude/longitude points
    R = 6371.0  # Radius of the Earth in kilometers
    lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def shortest_route(kwargs):
    all_locations = list(kwargs.keys())
    start_point = all_locations[0]  # Use the first key as the starting point
    route = [start_point]
    unvisited = all_locations[1:]  # All other points are initially unvisited

    while unvisited:
        last = kwargs[route[-1]]
        nearest = min(unvisited, key=lambda x: haversine_distance(last, kwargs[x]))
        # print("last -> ", last, "kwargs[x] -> ", kwargs[nearest])
        route.append(nearest)
        unvisited.remove(nearest)

    return route

def calculate_distances(route, locations):
    pairs_with_distances = []
    for start, end in zip(route, route[1:]):
        dist = haversine_distance(locations[start], locations[end])
        pairs_with_distances.append((start, end, f"{dist:.2f} km"))
        
    return pairs_with_distances

def format_routes(best_route):
    """Format routes for display."""
    formatted_output = ""
    for start, end, distance in best_route:
        formatted_output += (  
            f"<span style='margin-right:10px;'>{start}</span>"
            f"<span style='margin-right:10px;'>to</span>"
            f"<span style='margin-right:10px;'>{end}</span>"
            f"<span style='color:red;'>{distance}</span><br>"
        )
    return formatted_output

