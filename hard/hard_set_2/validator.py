"""
Validator for KV-Cached Multi-Head Attention - AI CODEFIX 2025 HARD_2

This script validates your implementation against test cases.

Usage:
    python validator.py --file kv_attention.py
    python validator.py --file kv_attention.py --verbose
    python validator.py --file kv_attention.py --test-file test_cases_hidden.json
"""

import argparse
import json
import sys
import importlib.util
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class AttentionValidator:
    """Validator for KV-Cached Multi-Head Attention implementation."""

    def __init__(self, module_path: str, test_file: str = "test_cases.json", verbose: bool = False):
        """
        Initialize validator.

        Args:
            module_path: Path to the Python file to test
            test_file: Path to test cases JSON file
            verbose: Whether to print detailed output
        """
        self.module_path = module_path
        self.test_file = test_file
        self.verbose = verbose
        self.module = None
        self.test_cases = []
        self.tolerance = 1e-4  # Tolerance for floating point comparisons

    def load_module(self) -> bool:
        """
        Dynamically load the Python module.

        Returns:
            True if successful, False otherwise
        """
        try:
            spec = importlib.util.spec_from_file_location("kv_attention_module", self.module_path)
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)

            # Verify required class exists
            if not hasattr(self.module, 'KVCachedMultiHeadAttention'):
                print("✗ Error: Module must contain 'KVCachedMultiHeadAttention' class")
                return False

            if self.verbose:
                print(f"✓ Successfully loaded module from {self.module_path}")

            return True
        except Exception as e:
            print(f"✗ Error loading module: {e}")
            return False

    def load_test_cases(self) -> bool:
        """
        Load test cases from JSON file.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.test_file, 'r') as f:
                data = json.load(f)

            # Handle both single test case and multiple test cases
            if isinstance(data, dict):
                if 'test_cases' in data:
                    self.test_cases = data['test_cases']
                elif 'test_case' in data:
                    self.test_cases = [data['test_case']]
                else:
                    print(f"✗ Error: Invalid test file format")
                    return False
            elif isinstance(data, list):
                self.test_cases = data
            else:
                print(f"✗ Error: Test file must contain dict or list")
                return False

            if self.verbose:
                print(f"✓ Loaded {len(self.test_cases)} test case(s) from {self.test_file}")

            return True
        except FileNotFoundError:
            print(f"✗ Error: Test file '{self.test_file}' not found")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON: {e}")
            return False
        except Exception as e:
            print(f"✗ Error loading test cases: {e}")
            return False

    def tensor_from_data(self, data: Any) -> torch.Tensor:
        """
        Convert data (list or dict) to PyTorch tensor.

        Args:
            data: Data to convert (list, nested list, or dict with 'values' key)

        Returns:
            PyTorch tensor
        """
        if isinstance(data, dict):
            if 'values' in data:
                values = data['values']
                shape = data.get('shape', None)
                tensor = torch.tensor(values, dtype=torch.float32)
                if shape:
                    tensor = tensor.view(*shape)
                return tensor

        return torch.tensor(data, dtype=torch.float32)

    def run_test_case(self, test_case: Dict[str, Any], test_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Run a single test case.

        Args:
            test_case: Test case dictionary
            test_id: Test case ID for reporting

        Returns:
            Tuple of (passed, message, results_dict)
        """
        try:
            # Extract test parameters
            config = test_case.get('config', {})
            d_model = config.get('d_model', 64)
            num_heads = config.get('num_heads', 4)
            max_cache_len = config.get('max_cache_len', 2048)
            dropout = config.get('dropout', 0.1)

            # Create model
            model_class = self.module.KVCachedMultiHeadAttention
            model = model_class(
                d_model=d_model,
                num_heads=num_heads,
                max_cache_len=max_cache_len,
                dropout=dropout
            )
            model.eval()  # Set to evaluation mode

            # Set random seed for reproducibility
            seed = test_case.get('seed', 42)
            torch.manual_seed(seed)
            np.random.seed(seed)

            # Load input tensors
            inputs = test_case.get('inputs', {})

            # Generate random inputs if placeholders are present
            if isinstance(inputs['query']['values'], str):
                inputs['query']['values'] = np.random.randn(*inputs['query']['shape']).tolist()
            if isinstance(inputs['key']['values'], str):
                inputs['key']['values'] = np.random.randn(*inputs['key']['shape']).tolist()
            if isinstance(inputs['value']['values'], str):
                inputs['value']['values'] = np.random.randn(*inputs['value']['shape']).tolist()
            
            # Handle cache placeholders
            cache_data = inputs.get('cache', None)
            if cache_data and isinstance(cache_data.get('key', {}).get('values'), str):
                 # For test 2, it says _FROM_TEST_1_OUTPUT_, but we can just use random
                 cache_data['key']['values'] = np.random.randn(*cache_data['key']['shape']).tolist()
                 cache_data['value']['values'] = np.random.randn(*cache_data['value']['shape']).tolist()

            query = self.tensor_from_data(inputs['query'])
            key = self.tensor_from_data(inputs['key'])
            value = self.tensor_from_data(inputs['value'])
            
            # Handle cache
            cache = None
            if cache_data is not None and cache_data != "null":
                k_cache = self.tensor_from_data(cache_data['key'])
                v_cache = self.tensor_from_data(cache_data['value'])
                
                # Reshape 3D [B, L, D] -> 4D [B, H, L, D/H] if needed
                k_cache_3d = k_cache
                v_cache_3d = v_cache
                
                if k_cache.dim() == 3:
                    B, L, D = k_cache.shape
                    head_dim = D // num_heads
                    # Assume [B, L, D] -> [B, L, H, D/H] -> [B, H, L, D/H]
                    k_cache_4d = k_cache.view(B, L, num_heads, head_dim).permute(0, 2, 1, 3)
                    v_cache_4d = v_cache.view(B, L, num_heads, head_dim).permute(0, 2, 1, 3)
                else:
                    k_cache_4d = k_cache
                    v_cache_4d = v_cache
                
                cache = {
                    'key': k_cache_4d,
                    'value': v_cache_4d
                }
                
                cache_ref = {
                    'key': k_cache_3d,
                    'value': v_cache_3d
                }
            else:
                cache_ref = None

            use_causal_mask = inputs.get('use_causal_mask', True)

            # Run forward pass
            with torch.no_grad():
                output, new_cache = model(query, key, value, cache=cache, use_causal_mask=use_causal_mask)

            # Check if expected outputs exist or need generation
            expected = test_case.get('expected', None)
            
            # Reference Implementation for validation
            import torch.nn.functional as F
            def reference_mha(q, k, v, cache_k, cache_v, mask_causal):
                B, Lq, _ = q.shape
                _, Lk_new, _ = k.shape
                
                head_dim = d_model // num_heads
                scale = head_dim ** 0.5
                
                # Projections
                Q = F.linear(q, model.q_proj.weight, model.q_proj.bias)
                K = F.linear(k, model.k_proj.weight, model.k_proj.bias)
                V = F.linear(v, model.v_proj.weight, model.v_proj.bias)
                
                # Split heads
                Q = Q.view(B, Lq, num_heads, head_dim).transpose(1, 2)
                K = K.view(B, Lk_new, num_heads, head_dim).transpose(1, 2)
                V = V.view(B, Lk_new, num_heads, head_dim).transpose(1, 2)
                
                # Concatenate cache (expecting 4D projected cache)
                if cache_k is not None:
                    # cache_k is [B, H, L_cache, D_H]
                    K = torch.cat([cache_k, K], dim=2)
                    V = torch.cat([cache_v, V], dim=2)
                
                # Update Lk to total length
                Lk = K.shape[2]
                
                # Scores
                scores = torch.matmul(Q, K.transpose(-2, -1)) / scale
                
                # Mask
                if mask_causal:
                    # Create mask: [Lq, Lk]
                    # i (query) can attend to j (key) if j <= i + offset
                    offset = Lk - Lq
                    mask = torch.ones(Lq, Lk, device=q.device)
                    for i in range(Lq):
                        for j in range(Lk):
                            if j > i + offset:
                                mask[i, j] = 0
                    mask = mask.view(1, 1, Lq, Lk)
                    scores = scores.masked_fill(mask == 0, float('-inf'))
                
                # Softmax
                attn = F.softmax(scores, dim=-1)
                
                # Output
                out = torch.matmul(attn, V)
                
                # Merge heads
                out = out.transpose(1, 2).contiguous().view(B, Lq, d_model)
                
                # Out projection
                out = F.linear(out, model.out_proj.weight, model.out_proj.bias)
                return out

            # Run reference
            cache_k = cache['key'] if cache else None
            cache_v = cache['value'] if cache else None
            ref_output = reference_mha(query, key, value, cache_k, cache_v, use_causal_mask)
            
            # Validate output values against reference
            output_diff = torch.abs(output - ref_output).max().item()
            if output_diff > self.tolerance:
                return (
                    False,
                    f"✗ Test #{test_id} - Output mismatch with reference: max diff = {output_diff:.6f}",
                    {'max_diff': output_diff}
                )

            # All validations passed
            return (
                True,
                f"✓ Test #{test_id} '{test_case.get('name', 'unnamed')}' - PASSED",
                {
                    'output_shape': list(output.shape),
                    'max_output_diff': output_diff,
                    'cache_key_shape': list(new_cache['key'].shape) if new_cache.get('key') is not None else None
                }
            )

        except Exception as e:
            import traceback
            error_msg = str(e)
            if self.verbose:
                error_msg += "\n" + traceback.format_exc()
            return (
                False,
                f"✗ Test #{test_id} - Runtime error: {error_msg}",
                None
            )

    def run_all_tests(self) -> Tuple[int, int, List[str]]:
        """
        Run all test cases.

        Returns:
            Tuple of (passed_count, total_count, messages)
        """
        passed = 0
        total = len(self.test_cases)
        messages = []

        for i, test_case in enumerate(self.test_cases, 1):
            success, message, results = self.run_test_case(test_case, i)
            messages.append(message)

            if self.verbose and results:
                messages.append(f"  Results: {results}")

            if success:
                passed += 1

        return passed, total, messages

    def validate(self) -> bool:
        """
        Run complete validation.

        Returns:
            True if all tests pass, False otherwise
        """
        print("=" * 70)
        print("KV-Cached Multi-Head Attention - Validator")
        print("=" * 70)

        # Load module
        if not self.load_module():
            return False

        # Load test cases
        if not self.load_test_cases():
            return False

        print(f"\nRunning {len(self.test_cases)} test case(s)...\n")

        # Run tests
        passed, total, messages = self.run_all_tests()

        # Print results
        for msg in messages:
            print(msg)

        print("\n" + "=" * 70)
        print(f"Results: {passed}/{total} tests passed")
        print("=" * 70)

        if passed == total:
            print("✓ All tests passed! Great job!")
            return True
        else:
            print(f"✗ {total - passed} test(s) failed. Keep debugging!")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate KV-Cached Multi-Head Attention implementation"
    )
    parser.add_argument(
        '--file',
        type=str,
        default='kv_attention.py',
        help='Path to the Python file to validate (default: kv_attention.py)'
    )
    parser.add_argument(
        '--test-file',
        type=str,
        default='test_cases.json',
        help='Path to test cases JSON file (default: test_cases.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed output'
    )

    args = parser.parse_args()

    # Resolve paths relative to script location if not absolute
    base_dir = Path(__file__).parent.absolute()
    
    module_path = Path(args.file)
    if not module_path.is_absolute():
        module_path = base_dir / module_path
        
    test_file_path = Path(args.test_file)
    if not test_file_path.is_absolute():
        test_file_path = base_dir / test_file_path

    # Create validator
    validator = AttentionValidator(
        module_path=str(module_path),
        test_file=str(test_file_path),
        verbose=args.verbose
    )

    # Run validation
    success = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
