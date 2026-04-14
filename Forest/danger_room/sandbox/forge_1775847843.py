```python
def safe_filter(elements):
    # A better filter function using a set for O(1) lookups instead of list's linear time complexity
    return {element for element in elements if isinstance(element, (int, float)) and not np.isnan(np.array([element]))}
```