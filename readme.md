# Heatmap Generator

## Features

- **Interactive Heatmap**: View an interactive heatmap in your browser, showcasing the distribution of player cities.
  The intensity of the heatmap represents the number of cities in a given cell.
    - **Dynamic Sizing**: The heatmap size adjusts dynamically based on the minimum and maximum coordinates derived from
      the data.
    - **Hover Details**: Hover over each cell to see the number of cities and their coordinates.
- **Island Clustering**: Groups nearby islands into clusters if they are within a configurable distance and contain a
  minimum number of
  cities. The final result is a markdown-formatted list of clusters.
    - **Configurable**: There are various configurable settings for the clusters generation. Take a look at
      the `user_config.json` file!

## Data

The data is sourced from the Ikalogs map site. Due to the presence of a JavaScript script that loads the data, direct
HTML fetching is not feasible. Instead, we use Selenium to simulate user interactions and extract the necessary data.
Note: This script uses the Firefox Driver for Selenium by default.

- **Data Caching**: After the initial data load, the information is parsed and saved into a JSON file
  named `{alliance_name}.json`. If you wish to fetch new data, you need delete this file and run the script again.

### Configuration

You can configure the script's behavior through the `user_config.json` file. The settings include:

- **`alliance_name`**: Name of the alliance you'd like to run this on.
- **`max_cluster_distance`**: Defines the maximum distance between islands that are considered part of the same cluster.
  A value of 1 means only adjacent islands are clustered together.
- **`min_cities_on_island_for_cluster`**: Specifies the minimum number of cities an island must have to be included in a
  cluster.
- **`min_total_cities_for_cluster`**: Sets a threshold for the total number of cities in a cluster. Clusters with fewer
  cities than this value will be excluded.

## Getting Started

1. **Install Dependencies**:
   Make sure you have Python 3.10+ and pip installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```


2. **Configure Settings**:
   Update the `user_config.json` file with your alliance name and clustering settings.


3. **Run the Script**:
   Execute the `code/generator.py` file to generate the heatmap and perform clustering:
   ```bash
   python code/generator.py
   ```

4. **View the Results**:
   - Results for the island clustering can be viewed inside the `data/{alliance_name}_island_clusters.md` file.
   - Results for the heatmap can be viewed in the browser (a new tab should have opened up for you with the plotly heatmap)

![Heatmap Example](readme_images/heatmap_example.png)
![City Clusters Example](readme_images/city_clusters_example.png)