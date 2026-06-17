# Ubiquitous Language

## Image Processing

- **Source image**: The image the user selects before background removal.
- **Result image**: The transparent PNG created after background removal.
- **Preview**: The on-screen rendering of the source image or result image.
- **Processing stage**: A named step in the background-removal flow, such as loading, removing, saving, or done.
- **Known progress**: A progress value for work the app can measure directly.
- **Busy progress**: An indeterminate progress state for work inside `rembg` where the app cannot know the exact percentage.
- **Output path**: The generated file path that ends in `_nobg.png`.
