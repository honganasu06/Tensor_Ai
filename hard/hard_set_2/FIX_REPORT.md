# Fix Report: KV-Cached Multi-Head Attention

This document details the fixes applied to `kv_attention.py` to correct the implementation of KV-Cached Multi-Head Attention.

## Summary of Changes

The original implementation contained several critical bugs affecting tensor shapes, mathematical correctness, and logic flow. All identified bugs have been fixed in place.

### 1. Scaling Factor
- **Bug**: `self.scale` was set to `self.head_dim`.
- **Fix**: Changed to `self.head_dim ** 0.5` (square root of head dimension) to match the standard scaled dot-product attention formula.

### 2. Tensor Reshaping (Head Splitting)
- **Bug**: `_split_heads` used `view(batch, num_heads, seq_len, head_dim)` on a tensor shaped `[batch, seq_len, d_model]`. This incorrect view scrambled the data across heads and sequence positions.
- **Fix**: Changed to `view(batch, seq_len, num_heads, head_dim)` followed by `permute(0, 2, 1, 3)` to correctly arrange dimensions to `[batch, num_heads, seq_len, head_dim]`.

### 3. Cache Concatenation Logic
- **Bug**: The code attempted to concatenate cached keys/values with new ones using `dim=2` on 3D tensors `[batch, seq_len, d_model]`. This was dimensionally incorrect and happened before head splitting.
- **Fix**: Moved the cache concatenation logic *after* `_split_heads`. Now, it correctly concatenates the 4D tensors `[batch, num_heads, seq_len, head_dim]` along the sequence dimension (`dim=2`).

### 4. Matrix Multiplication
- **Bug**: The attention score calculation used `K.transpose(1, 2)`. For 4D tensors `[batch, heads, seq, dim]`, this swapped the head and sequence dimensions, leading to invalid matrix multiplication shapes or incorrect results.
- **Fix**: Changed to `K.transpose(-2, -1)` to correctly transpose the last two dimensions (sequence length and head dimension) for the operation $Q K^T$.

### 5. Softmax Dimension
- **Bug**: `F.softmax` was applied on `dim=2` (the query sequence length dimension in the scores tensor).
- **Fix**: Changed to `dim=-1` (the key sequence length dimension) to correctly normalize attention weights over the keys.

### 6. Causal Masking
- **Bug**: The offset calculation `cache_len + 1` was off-by-one, and the mask condition `j <= i + cache_len` was inconsistent with the offset.
- **Fix**: Corrected offset to `cache_len` and the mask condition to `j <= i + offset`. Also changed the mask data type to `.bool()` for proper usage with `masked_fill`.

### 7. Cache Update
- **Bug**: The code attempted to store `K[:, :, -seq_len:, :]` in the cache. While intended to store new tokens, the logic was flawed and the read logic was also broken.
- **Fix**: Updated to store the full concatenated `K` and `V` tensors in the cache, ensuring the entire context history is preserved for future steps.

## Verification

The fixed code has been verified by running the internal test block, which confirms:
- Correct output shapes for initial forward pass.
- Correct cache growth and reuse for subsequent forward passes (simulating autoregressive generation).
