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
from data_manager import load_json_from_file, fetch_or_load_data, validate_browser_type, validate_alliance_name


def create_interactive_heatmap(coordinates_list: list, alliance_name: str):
    if not coordinates_list:
        print("No coordinate data found.")
        return

    # Set fixed grid bounds (1:1 to 100:100)
    min_x, max_x = 1, 100
    min_y, max_y = 1, 100

    # Create a 100x100 heatmap grid
    grid_size = 100
    island_heatmap = np.zeros((grid_size, grid_size))

    # Populate the heatmap with coordinates, adjusting for the fixed grid size
    for x, y in coordinates_list:
        if min_x <= x <= max_x and min_y <= y <= max_y:
            island_heatmap[y - min_y, x - min_x] += 1

    # Create a DataFrame for Plotly with the fixed coordinates
    df = pd.DataFrame(island_heatmap,
                      index=[f'{y + min_y}' for y in range(grid_size)],
                      columns=[f'{x + min_x}' for x in range(grid_size)])

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
        xaxis=dict(scaleanchor="y", range=[1, 100]),  # Force x-axis range from 1 to 100
        yaxis=dict(constrain='domain', range=[1, 100]),  # Force y-axis range from 1 to 100
        coloraxis_colorbar=dict(title=f'Amount of cities')
    )

    fig.update_traces(
        texttemplate='%{text}',  # Display text in cells
        textfont_size=10  # Adjust text size
    )

    fig.show()


def main():
    config_data = load_json_from_file('../user_config.json')

    browser_type = config_data.get('browser_type')
    validate_browser_type(browser_type)

    alliance_name = config_data.get('alliance_name')
    validate_alliance_name(alliance_name)

    coordinates_list, was_loaded_from_cache = fetch_or_load_data(alliance_name, browser_type)

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
