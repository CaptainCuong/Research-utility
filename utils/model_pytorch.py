import torch.nn as nn

def pytorch_total_params(model):
    num_params = sum(p.numel() for p in model.parameters())
    return num_params

# Example usage
model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 1))
print("Total number of parameters: ", pytorch_total_params(model))