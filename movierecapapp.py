import gradio as gr
import subprocess
import os
from moviepy import VideoFileClip
from moviepy.video.fx import all as vfx


OUTPUT_FILE = "output.mp4"

def process_video(input_video):
    try:
        clip = VideoFileClip(input_video)

        # 1. Horizontal flip
        clip = clip.fx(vfx.mirror_x)

        # 2. Slight zoom (crop center)
        clip = clip.fx(vfx.crop, x_center=clip.w/2, y_center=clip.h/2,
                       width=int(clip.w * 0.95), height=int(clip.h * 0.95))
        clip = clip.resize((clip.w, clip.h))

        # 3. Slight speed change
        clip = clip.fx(vfx.speedx, 1.03)

        temp_video = "temp.mp4"
        clip.write_videofile(temp_video, codec="libx264", audio_codec="aac")

        # 4. FFmpeg filters (brightness, contrast, slight noise + audio pitch)
        final_output = OUTPUT_FILE

        ffmpeg_command = [
            "ffmpeg",
            "-i", temp_video,
            "-vf", "eq=brightness=0.03:contrast=1.05,noise=alls=5:allf=t",
            "-af", "asetrate=44100*1.02,aresample=44100",
            "-map_metadata", "-1",  # 5. Remove metadata
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            final_output
        ]

        subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        os.remove(temp_video)

        return final_output

    except Exception as e:
        return str(e)


app = gr.Interface(
    fn=process_video,
    inputs=gr.Video(label="Upload Video"),
    outputs=gr.Video(label="Processed Video"),
    title="Video Editor App",
    description="Upload a video and apply creative edits (flip, zoom, speed, color adjustments)."
)

if __name__ == "__main__":
    app.launch()
