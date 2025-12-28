from src.audio_utils import get_audio_duration
from src.video import create_background
from src.render import render_video
from src.captions import create_srt

audio = "test_voice.mp3"
duration = get_audio_duration(audio)

bg = "assets/bg.mp4"
srt = "assets/captions.srt"
out = "outputs/final_short.mp4"

script_text = (
    "Your brain releases dopamine when something feels new. "
    "That is why short videos feel addictive. "
    "Each swipe gives a small reward. "
    "Subscribe for more facts like this."
)

create_background(duration, bg)
create_srt(script_text, duration, srt)
render_video(bg, audio, srt, out)

print("Video created:", out)
