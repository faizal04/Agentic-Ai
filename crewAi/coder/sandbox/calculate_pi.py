def calculate_series(n):
    total = 0.0
    for i in range(n):
        # The series is 1/1 - 1/3 + 1/5 - 1/7 + ...
        # The denominator follows 2*i + 1
        # The sign alternates: (-1)^i
        # Optimization: use if i % 2 == 0 to avoid exponentiation
        if i % 2 == 0:
            total += 1 / (2 * i + 1)
        else:
            total -= 1 / (2 * i + 1)
    return total * 4

n_terms = 1_000_000
result = calculate_series(n_terms)
print(f"Result with {n_terms} terms: {result}")
