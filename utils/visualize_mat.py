import matplotlib.pyplot as plt
import numpy as np
import torch
from seaborn import heatmap

def save_mat_plt(tensor, path):
    '''
    tensor: a 2-dimension tensor
    path: directory in which tensor is stored
    '''
    tensor = to_numpy(tensor)
    plt.matshow(tensor, fignum=100)
    plt.gca().set_aspect('auto')
    plt.savefig(path, dpi=600)

def save_heatmap_sns(tensor, path):
    tensor = to_numpy(tensor)
    heatmap(tensor,cmap="YlGnBu")
    plt.savefig(path, dpi=600)

def to_numpy(tensor):
    '''
    Check whether type of tensor is torch.Tensor
    Convert to numpy
    '''
    if type(tensor) is torch.Tensor:
        assert len(tensor.shape) == 2
        tensor = tensor.cpu().numpy()
    else:
        raise Exception(f'Undefined type: {type(tensor)}')

    return tensor