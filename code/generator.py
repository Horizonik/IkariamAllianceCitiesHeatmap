import plotly.express as px
import pandas as pd
import numpy as np

from island_clustering import (
    filter_islands_by_city_count,
    cluster_islands,
    count_cities_per_island,
    filter_clusters_by_city_count,
    format_clusters,
    export_clusters_to_markdown
)
from data_manager import load_json, fetch_or_load_data


def create_interactive_heatmap(coordinates_list: list, alliance_name: str):
    if not coordinates_list:
        print("No coordinate data found.")
        return

    min_x = min(coord[0] for coord in coordinates_list)
    max_x = max(coord[0] for coord in coordinates_list)
    min_y = min(coord[1] for coord in coordinates_list)
    max_y = max(coord[1] for coord in coordinates_list)

    map_width = max_x - min_x + 1
    map_height = max_y - min_y + 1

    map_size = max(map_width, map_height)
    island_heatmap = np.zeros((map_size, map_size))

    for x, y in coordinates_list:
        island_heatmap[y - min_y, x - min_x] += 1

    # Create a DataFrame for Plotly with the correct coordinates
    df = pd.DataFrame(island_heatmap,
                      index=[f'{y + min_y}' for y in range(map_size)],
                      columns=[f'{x + min_x}' for x in range(map_size)])

    # Melt the DataFrame to long format for Plotly
    df_melted = df.reset_index().melt(id_vars='index', var_name='X', value_name=f'{alliance_name} Cities')
    df_melted.rename(columns={'index': 'Y'}, inplace=True)

    # Create heatmap
    fig = px.density_heatmap(df_melted, x='X', y='Y', z=f'{alliance_name} Cities', color_continuous_scale='YlOrRd',
                             text_auto=True)

    # Update layout
    fig.update_layout(
        title=f"{alliance_name} Alliance City Distribution Heatmap",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        xaxis=dict(scaleanchor="y"),  # This ensures the x-axis maintains a 1:1 aspect ratio with the y-axis
        yaxis=dict(constrain='domain'),  # Ensure the y-axis scales with the domain
        coloraxis_colorbar=dict(title=f'Amount of cities')
    )

    fig.update_traces(
        texttemplate='%{text}',  # Display text in cells
        textfont_size=10  # Adjust text size
    )

    fig.show()


def main():
    config_data = load_json()

    alliance_name = config_data.get('alliance_name')
    if not alliance_name:
        raise ValueError("Alliance name not found in config.")

    coordinates_list, was_loaded_from_cache = fetch_or_load_data(alliance_name)

    # Apply filtering based on minimum cities before clustering
    min_cities_on_island_for_cluster = int(config_data.get('min_cities_on_island_for_cluster'))
    filtered_coordinates_list = filter_islands_by_city_count(coordinates_list, min_cities_on_island_for_cluster)

    create_interactive_heatmap(filtered_coordinates_list, alliance_name)

    # Calculate city clusters
    max_cluster_distance = int(config_data.get('max_cluster_distance'))

    clusters = cluster_islands(filtered_coordinates_list, max_distance=max_cluster_distance)
    city_counts = count_cities_per_island(filtered_coordinates_list)
    filtered_clusters = filter_clusters_by_city_count(clusters, city_counts, min_cities_on_island_for_cluster)

    min_total_cities_for_cluster = int(config_data.get('min_total_cities_for_cluster'))
    formatted_clusters = format_clusters(filtered_clusters, city_counts, min_total_cities_for_cluster)
    export_clusters_to_markdown(formatted_clusters, f"../data/{alliance_name}_island_clusters.md")


if __name__ == "__main__":
    main()
