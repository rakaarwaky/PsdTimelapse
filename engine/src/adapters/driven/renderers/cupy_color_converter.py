"""
GPU Color Space Converter using Native CuPy Operations.
Converts Float32 RGBA to NV12/RGB Uint8 in-place on GPU.
Fully vectorized to avoid JIT compilation dependency.
"""

import cupy as cp


class CupyColorConverter:
    def __init__(self) -> None:
        # Optimized CUDA C++ Kernel for BT.709 RGB to NV12 (Limited Range)
        self.kernel_code = r"""
        extern "C" __global__
        void rgba_to_nv12(const float* rgba, unsigned char* nv12, int width, int height) {
            int x = blockIdx.x * blockDim.x + threadIdx.x;
            int y = blockIdx.y * blockDim.y + threadIdx.y;

            if (x >= width || y >= height) return;

            int idx = y * width + x;
            int rgba_idx = idx * 4;

            // Input is RGB float [0.0, 1.0]
            float r = rgba[rgba_idx];
            float g = rgba[rgba_idx + 1];
            float b = rgba[rgba_idx + 2];

            // Y (BT.709 Limited Range: 16-235)
            // Y = 16 + 219 * (0.2126*R + 0.7152*G + 0.0722*B)
            float y_f = 16.0f + 219.0f * (0.2126f * r + 0.7152f * g + 0.0722f * b);
            unsigned char y_val = (unsigned char)fminf(fmaxf(y_f, 16.0f), 235.0f);
            nv12[idx] = y_val;

            // UV (BT.709 Limited Range: 16-240)
            if (x % 2 == 0 && y % 2 == 0) {
                // U = 128 + 224 * (-0.1146*R - 0.3854*G + 0.5*B)
                float u_f = 128.0f + 224.0f * (-0.1146f * r - 0.3854f * g + 0.5000f * b);
                // V = 128 + 224 * (0.5*R - 0.4542*G - 0.0458*B)
                float v_f = 128.0f + 224.0f * (0.5000f * r - 0.4542f * g - 0.0458f * b);

                unsigned char u = (unsigned char)fminf(fmaxf(u_f, 16.0f), 240.0f);
                unsigned char v = (unsigned char)fminf(fmaxf(v_f, 16.0f), 240.0f);

                int uv_idx = width * height + (y / 2) * width + x;
                nv12[uv_idx] = u;
                nv12[uv_idx + 1] = v;
            }
        }
        """
        self.kernel = cp.RawKernel(self.kernel_code, "rgba_to_nv12")

    def convert(self, rgba_ptr, width, height, output_buffer=None):
        """
        Convert RGBA (Float32) pointer to NV12 (Uint8) CuPy Array using RawKernel.
        """
        # Wrap input pointer
        # Size: width * height * 4 (channels) * 4 (float32 bytes)
        input_size_bytes = width * height * 4 * 4

        # UnownedMemory creates a pointer wrapper without allocation
        mem_ptr = cp.cuda.UnownedMemory(rgba_ptr, input_size_bytes, owner=None)
        memptr = cp.cuda.MemoryPointer(mem_ptr, 0)

        # Create array view from pointer
        # We process as flat float32 for simplicity in kernel indexing, or use logical shape
        # Kernel expects float* pointer so shape doesn't matter much for arg,
        # but we need 'rgba' array object to pass to kernel? NO.
        # RawKernel arguments can be: arrays, scalars, or pointers (int).
        # We can pass `rgba_ptr` (int) directly if we cast it in kernel?
        # No, CuPy RawKernel expects arrays usually.
        # But we can pass the array we created.
        rgba_arr = cp.ndarray((height, width, 4), dtype=cp.float32, memptr=memptr)

        # Output Buffer
        # If output_buffer is not provided, allocate new.
        # Ideally, reuse buffer to avoid malloc overhead!
        nv12_size = int(width * height * 1.5)

        if output_buffer is None:
            nv12_arr = cp.zeros(nv12_size, dtype=cp.uint8)
        else:
            nv12_arr = output_buffer

        # Grid/Block dims
        block = (32, 32, 1)
        grid = ((width + 31) // 32, (height + 31) // 32, 1)

        # Check output size
        if nv12_arr.size < nv12_size:
            raise ValueError("Output buffer too small for NV12 conversion")

        # Launch Kernel
        self.kernel(grid, block, (rgba_arr, nv12_arr, width, height))

        return nv12_arr
