from pyscrew.transformers import HandleDuplicatesTransformer
from pyscrew.utils.data_model import JsonFields


def test_basic_duplicate_removal(basic_screw_dataset):
    """Test removing duplicates at step boundaries."""
    transformer = HandleDuplicatesTransformer(handle_duplicates="first")
    result = transformer.transform(basic_screw_dataset)

    first_run = 0
    time_values = result.processed_data[JsonFields.Measurements.TIME][first_run]

    # Original length was 35 (5+15+10+5)
    # Should now be 32 because we removed 3 duplicates at step boundaries
    assert len(time_values) == 32

    # Check stats
    assert transformer._stats.total_removed == 3  # One at each step boundary
    assert transformer._stats.total_series == 1
    assert transformer._stats.total_points == 35  # Original points
    assert (
        transformer._stats.total_true_duplicates == 3
    )  # All our duplicates match exactly
    assert transformer._stats.total_value_differences == 0  # No value differences
