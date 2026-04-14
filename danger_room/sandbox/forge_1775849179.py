```python
def efficient_filter(data, criteria):
    # Minor optimization using a set for faster lookup instead of list comprehension with 'in' operator on potentially large lists
    return [item for item in data if all(key in crit for key, value in criterias.items() if (criteria[key] != None and not eval(f"{value} == {getattr(item, key)}")))]
```