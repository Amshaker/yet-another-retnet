from typing import Optional

import pytest
import torch
from torch import Tensor

from yet_another_retnet.retention import (
    MultiheadRetention,
    retention_parallel,
    retention_recurrent,
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.float32


def test_retention_parallel_forward():
    # TODO
    pass


def test_retention_recursive_forward():
    # TODO
    pass


@torch.no_grad()
@pytest.mark.parametrize("batch_size", [2])
@pytest.mark.parametrize("num_heads", [2, 4])
@pytest.mark.parametrize("seq_length", [16])
@pytest.mark.parametrize("hidden_dim", [4, 8])
def test_parallel_equals_recursive(
    batch_size: int,
    num_heads: int,
    seq_length: int,
    hidden_dim: int,
):
    size = (batch_size, num_heads, seq_length, hidden_dim)
    query = torch.randn(*size, device=DEVICE, dtype=DTYPE)
    key = torch.randn(*size, device=DEVICE, dtype=DTYPE)
    value = torch.randn(*size, device=DEVICE, dtype=DTYPE)

    y_parallel, _ = retention_parallel(query, key, value)

    y_recurrent = torch.zeros_like(y_parallel)
    prev_state: Optional[Tensor] = None
    for i in range(seq_length):
        q, k, v = query[:, :, i], key[:, :, i], value[:, :, i]
        y_recurrent[:, :, i], prev_state = retention_recurrent(q, k, v, prev_state)

    torch.testing.assert_close(y_parallel, y_recurrent)


def test_multihead_retention_forward_parallel():
    # TODO
    pass


def test_multihead_retention_forward_recursive():
    # TODO
    pass


@torch.no_grad()
@pytest.mark.parametrize("batch_size", [2])
@pytest.mark.parametrize("num_heads", [1, 2])
@pytest.mark.parametrize("seq_length", [8])
@pytest.mark.parametrize("embed_dim", [16, 32])
def test_multihead_parallel_equals_recursive(
    batch_size: int,
    num_heads: int,
    seq_length: int,
    embed_dim: int,
):
    size = (batch_size, seq_length, embed_dim)
    query = torch.randn(*size, device=DEVICE, dtype=DTYPE)
    key = torch.randn(*size, device=DEVICE, dtype=DTYPE)
    value = torch.randn(*size, device=DEVICE, dtype=DTYPE)
    mhr = MultiheadRetention(embed_dim, num_heads, device=DEVICE, dtype=DTYPE).eval()

    y_parallel, _ = mhr.forward_parallel(query, key, value)

    y_recurrent = torch.zeros_like(y_parallel)
    prev_state: Optional[Tensor] = None
    for i in range(seq_length):
        q, k, v = query[:, i], key[:, i], value[:, i]
        y_recurrent[:, i], prev_state = mhr.forward_recurrent(
            q, k, v, seq_idx=i, prev_state=prev_state
        )

    torch.testing.assert_close(y_parallel, y_recurrent)
