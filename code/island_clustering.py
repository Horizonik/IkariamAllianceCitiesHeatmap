from itertools import product
from collections import defaultdict


def cluster_islands(coordinates_list: list, max_distance=2) -> list:
    coord_set = set(map(tuple, coordinates_list))
    visited = set()
    clusters = []

    def dfs(coord: tuple, cluster: list):
        stack = [coord]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            cluster.append(current)
            for dx, dy in product(range(-max_distance, max_distance + 1), repeat=2):
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in coord_set and neighbor not in visited:
                    stack.append(neighbor)

    for coord in coord_set:
        if coord not in visited:
            cluster = []
            dfs(coord, cluster)
            clusters.append(cluster)

    return clusters


def count_cities_per_island(coordinates_list: list) -> dict:
    city_counts = defaultdict(int)
    for coord in coordinates_list:
        city_counts[tuple(coord)] += 1
    return dict(city_counts)


def filter_islands_by_city_count(coordinates_list: list, min_cities: int) -> list:
    city_counts = count_cities_per_island(coordinates_list)
    return [coord for coord in coordinates_list if city_counts[tuple(coord)] >= min_cities]


def filter_clusters_by_city_count(clusters: list, city_counts: dict, min_cities: int) -> list[str]:
    filtered_clusters = []
    for cluster in clusters:
        if any(city_counts.get(tuple(island), 0) >= min_cities for island in cluster):
            filtered_clusters.append(cluster)
    return filtered_clusters


def format_clusters(clusters: list, city_counts: dict, min_total_cities_for_cluster: int) -> list[str]:
    formatted_clusters = []
    cluster_index = 1

    for cluster in clusters:
        cluster_name = f"City Cluster {chr(65 + cluster_index - 1)}"
        total_cities = sum(city_counts.get(tuple(island), 0) for island in cluster)

        if total_cities < min_total_cities_for_cluster:
            continue

        cluster_str = [f"#### {cluster_name} - total of {total_cities}"]
        for island in cluster:
            count = city_counts.get(tuple(island), 0)
            cluster_str.append(f"- {island[0]}:{island[1]} -> {count} cities")

        formatted_clusters.append("\n".join(cluster_str))
        cluster_index += 1

    return formatted_clusters


def export_clusters_to_markdown(formatted_clusters: list[str], file_path: str = 'island_clusters.md'):
    with open(file_path, 'w') as file:
        file.write("# City Clusters:\n")
        for cluster in formatted_clusters:
            file.write(f"{cluster}\n\n")
