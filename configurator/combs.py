import itertools

# Example usage
args1 = 1
args2 = ['A', 'B']
eta = [[1, 3], [3, 6]]
all_combinations = list(itertools.product(args1, args2, eta))

print(len(all_combinations))