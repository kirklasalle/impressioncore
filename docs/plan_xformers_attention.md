# Plan: Implement Memory-Efficient Attention using xFormers

1.  **Goal:** Replace the standard `torch.nn.MultiheadAttention` in `src/diffusion/unet.py` with `xformers.ops.memory_efficient_attention` to reduce VRAM usage, targeting the GTX 1050 Ti.
2.  **Prerequisite:** Add `xformers` as a project dependency and ensure it's installed in the environment.
3.  **Detailed Steps:**
    *   **(Code Mode Task 1) Add `xformers` to `requirements.txt`:** Add a line for `xformers`. *Note: The specific version might need adjustment based on the exact PyTorch and CUDA versions installed in the user's environment.*
    *   **(User Task) Install Dependency:** After `requirements.txt` is updated, the user needs to install `xformers` (e.g., `pip install -r requirements.txt` or `pip install xformers`). *This step might require troubleshooting depending on the environment.*
    *   **(Code Mode Task 2) Modify `AttentionBlock` in `src/diffusion/unet.py`:**
        *   Import `xformers.ops as xops`.
        *   Remove the `torch.nn.MultiheadAttention` layer.
        *   Add `nn.Linear` projection layers for query (Q), key (K), and value (V). These layers will take the input channels and project them to the embedding dimension needed for attention.
        *   In the `forward` method:
            *   Reshape the input feature map `h_` from `(B, C, H, W)` to `(B, S, C)` where `S = H * W` (sequence length).
            *   Apply the Q, K, V linear projections to the reshaped input.
            *   Call `xops.memory_efficient_attention(query, key, value, attn_bias=None)`. *Note: We might need to handle attention masks or biases later if required.*
            *   Reshape the output attention tensor back to the original feature map format `(B, C, H, W)`.
    *   **(Code Mode Task 3) Testing:** Update the `if __name__ == '__main__':` block in `unet.py` to instantiate the modified `UNet` and run a dummy forward pass to catch structural errors.
    *   **(Future Task) Evaluation:** Once the model is trainable/runnable, benchmark memory usage and performance against the previous standard attention implementation.
    *   **(Code Mode Task 4) Documentation:** Update the `AttentionBlock` docstring in `unet.py` and add details about `xformers` usage to `docs/memory_optimization_strategies.md` (or create it if it doesn't exist).

4.  **Diagram:**

    ```mermaid
    graph TD
        A[Start Memory-Efficient Attention Task] --> B[Plan: Add xformers to requirements.txt];
        B --> C[Plan: User Installs xformers];
        C --> D[Plan: Modify AttentionBlock in unet.py];
        D --> E[Plan: Use xops.memory_efficient_attention];
        E --> F[Plan: Test Implementation Structure];
        F --> G[Plan: Document Changes];
        G --> H[Future: Evaluate Performance/Memory];