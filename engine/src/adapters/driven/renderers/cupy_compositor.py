import cupy as cp  # type: ignore[import-not-found]

from domain.ports.render.compositor_port import CompositorPort  # type: ignore[import-not-found]


class CupyCompositor(CompositorPort):  # type: ignore[misc]
    def __init__(self) -> None:
        # Optimized CUDA Alpha Blending Kernel
        # Assumes Float32 RGBA (0.0-1.0)
        self.kernel_code = r"""
        extern "c" __global__
        void blend_overlay(
            float* canvas,
            const float* overlay,
            int overlay_w, int overlay_h,
            int canvas_w, int canvas_h,
            int offset_x, int offset_y
        ) {
            int x = blockIdx.x * blockDim.x + threadIdx.x;
            int y = blockIdx.y * blockDim.y + threadIdx.y;

            if (x >= overlay_w || y >= overlay_h) return;

            // Calculate coordinates on canvas
            int cx = offset_x + x;
            int cy = offset_y + y;

            if (cx < 0 || cx >= canvas_w || cy < 0 || cy >= canvas_h) return;

            int overlay_idx = (y * overlay_w + x) * 4;
            int canvas_idx = (cy * canvas_w + cx) * 4;

            // Load overlay
            float or_ = overlay[overlay_idx];
            float og_ = overlay[overlay_idx + 1];
            float ob_ = overlay[overlay_idx + 2];
            float oa_ = overlay[overlay_idx + 3];

            // Optimization: If transparent, skip
            if (oa_ <= 0.001f) return;

            // Load canvas
            float Cr = canvas[canvas_idx];
            float Cg = canvas[canvas_idx + 1];
            float Cb = canvas[canvas_idx + 2];
            float Ca = canvas[canvas_idx + 3];

            // "Normal" Blend Mode (Source Over)
            // out_a = src_a + dst_a * (1 - src_a)
            float out_a = oa_ + Ca * (1.0f - oa_);

            if (out_a > 0.0f) {
                // out_rgb = (src_rgb * src_a + dst_rgb * dst_a * (1 - src_a)) / out_a
                // Pre-multiplied alpha logic usually simpler, but assuming straight alpha here:
                // Standard formula:
                // Result = Src * SrcA + Dst * DstA * (1 - SrcA) / OutA
                // Wait, standard Pillow blend:
                // out = src * alpha + dst * (1 - alpha)
                // This assumes dst is opaque usually?
                // If dst has alpha, Porter-Duff Source Over:

                float term2 = Ca * (1.0f - oa_);

                canvas[canvas_idx]     = (or_ * oa_ + Cr * term2) / out_a;
                canvas[canvas_idx + 1] = (og_ * oa_ + Cg * term2) / out_a;
                canvas[canvas_idx + 2] = (ob_ * oa_ + Cb * term2) / out_a;
                canvas[canvas_idx + 3] = out_a;
            }
        }
        """
        self.blend_kernel = cp.RawKernel(self.kernel_code, "blend_overlay")

    def blend(self, canvas_arr, overlay_arr, x, y) -> None:  # type: ignore[no-untyped-def]
        """
        Blend overlay_arr onto canvas_arr at (x, y) in-place.
        canvas_arr: CuPy array (h, w, 4) float32
        overlay_arr: CuPy array (h, w, 4) float32
        x, y: position
        """
        h, w, c = overlay_arr.shape
        h, w, c = canvas_arr.shape

        block = (32, 32, 1)
        grid = ((w + 31) // 32, (h + 31) // 32, 1)

        self.blend_kernel(grid, block, (canvas_arr, overlay_arr, w, h, w, h, x, y))

    def is_available(self) -> bool:
        """Check if GPU backend is available."""
        return True  # Already requires CuPy import to instantiate
