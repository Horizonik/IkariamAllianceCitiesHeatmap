import pytest

from code.generator import create_interactive_heatmap
from code.data_manager import fetch_or_load_data, load_json_from_file

from code.island_clustering import (
    filter_islands_by_city_count,
    cluster_islands,
    count_cities_per_island,
    filter_clusters_by_city_count,
    format_clusters
)


@pytest.fixture
def mock_config():
    return load_json_from_file('mock_data/mock_config.json')


@pytest.fixture
def mock_filtered_coordinates(mock_config):
    mock_coordinates = load_json_from_file('mock_data/fabricated_coordinates.json')
    return filter_islands_by_city_count(
        mock_coordinates,
        mock_config.get('min_cities_on_island_for_cluster')
    )


class TestIkariamAllianceHeatmap:
    def test_can_read_user_config_successfully(self):
        config_data = load_json_from_file('../../user_config.json')
        assert config_data is not None, "Failed when trying to read user_config.json!"

    def test_data_is_scraped_successfully(self, mock_config):
        """
        This tests verifies that we have retrieved island data successfully.
        Note: If the -SF- alliance ceases to exist, this test will fail!
        """

        coordinates_list, was_loaded_from_cache = fetch_or_load_data(
            mock_config.get('alliance_name'),
            mock_config.get('browser_type'),
            False
        )

        assert coordinates_list is not None, "Could not fetch coordinates!"

    def test_heatmap_is_generated_from_data_successfully(self, mock_config, mock_filtered_coordinates):
        """Verifies that the heatmap can be generated without any errors"""
        create_interactive_heatmap(mock_filtered_coordinates, mock_config.get('alliance_name'))

    def test_island_clustering_produces_results(self, mock_config, mock_filtered_coordinates):
        """Verifies that we get a result from the island clustering calculation (Doesn't verify if it's correct!)"""

        clusters = cluster_islands(mock_filtered_coordinates, mock_config.get('max_cluster_distance'))
        city_counts = count_cities_per_island(mock_filtered_coordinates)
        filtered_clusters = filter_clusters_by_city_count(clusters, city_counts,
                                                          mock_config.get('min_cities_on_island_for_cluster'))

        min_total_cities_for_cluster = int(mock_config.get('min_total_cities_for_cluster'))
        formatted_clusters = format_clusters(filtered_clusters, city_counts, min_total_cities_for_cluster)

        assert formatted_clusters is not None, "Failed when trying to calculate island clusters!"
