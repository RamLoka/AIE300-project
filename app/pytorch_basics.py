import torch

tensor_from_list = torch.tensor([1, 2, 3, 4])

random_tensor = torch.randn(2, 3)

print("Tensor from list:")
print(tensor_from_list)

print("\nRandom tensor:")
print(random_tensor)

a = torch.tensor([[1, 2], [3, 4]], dtype=torch.float32)
b = torch.tensor([[5, 6], [7, 8]], dtype=torch.float32)

addition_result = a + b

matrix_mult_result = torch.matmul(a, b)

print("\nAddition Result:")
print(addition_result)

print("\nMatrix Multiplication Result:")
print(matrix_mult_result)

x = torch.tensor(3.0, requires_grad=True)

y = x ** 2 + 2 * x + 1

y.backward()

print("\nAutograd Example:")
print(f"x = {x.item()}")
print(f"y = {y.item()}")
print(f"dy/dx = {x.grad.item()}")