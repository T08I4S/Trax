import moviepy
import traceback

print("MoviePy version:", getattr(moviepy, "__version__", "unknown"))
try:
    from moviepy.editor import AudioFileClip, concatenate_audioclips
    print("moviepy.editor exists!")
except Exception as e:
    print("moviepy.editor failed:", e)

try:
    from moviepy import AudioFileClip, concatenate_audioclips
    print("moviepy direct imports exist!")
except Exception as e:
    print("moviepy direct imports failed:", e)
