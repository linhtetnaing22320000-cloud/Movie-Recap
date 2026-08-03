import streamlit as st
import os
import requests
from moviepy import VideoFileClip, AudioFileClip, vfx

st.set_page_config(page_title="Movie Recap Video Editor", layout="centered")

st.title("🎬 Movie Recap Video & Voiceover Editor")
st.write("TikTok Unoriginal Content AI လွတ်အောင် အရောင်နှင့် အမြန်နှုန်း ချိန်ညှိပေးသော စနစ်။")

# ဖိုင်များ တင်ခိုင်းခြင်း
uploaded_video = st.file_uploader("1. Movie Recap ဗီဒီယိုဖိုင်ကို တင်ပါ (mp4, mov)", type=["mp4", "mov", "avi"])
uploaded_audio = st.file_uploader("3. မြန်မာအသံ AI Voiceover MP3 ဖိုင်ကို တင်ပါ", type=["mp3", "wav"])

# AI စစ်ဆေးမှုကို ရှောင်ရှားရန် ထပ်ဆောင်း ဆက်တင်များ
st.subheader("🛡️ TikTok Unoriginal Content Protection")
adjust_color = st.checkbox("✨ ဗီဒီယိုအရောင်နှင့် တောက်ပမှုကို အနည်းငယ်ပြောင်းလဲမည် (AI ကျော်ရန်)", value=True)
video_speed_factor = st.slider("ဗီဒီယို အမြန်နှုန်း (1.02x သို့မဟုတ် 1.05x ထားပါက AI ရှောင်ရန် ပိုကောင်းသည်)", 1.0, 1.1, 1.03)

# အသံ အမြန်နှုန်း ညှိရန်
speed_factor = st.slider("4. Voiceover အသံ အမြန်နှုန်း (ခပ်သွက်သွက်ပြောရန် 1.1x - 1.3x)", 1.0, 1.5, 1.2)

# Telegram Bot အတွက် အချက်အလက်များ
TELEGRAM_BOT_TOKEN = "8210372462:AAHcx7fDDndpk9RPE5Gsu6f-k2iYC1d0x7Q"
TELEGRAM_CHAT_ID = "1604996232"

def send_telegram_notification(message):
    """Telegram Bot မှတဆင့် Noti ပို့မည့် Function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False

if uploaded_video is not None and uploaded_audio is not None:
    
    video_path = "temp_input_video.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_video.getbuffer())
        
    audio_path = "temp_input_audio.mp3"
    with open(audio_path, "wb") as f:
        f.write(uploaded_audio.getbuffer())
        
    st.success("ဖိုင်များ အောင်မြင်စွာ တင်ပြီးပါပြီ။")
    
    if st.button("🚀 ဗီဒီယိုနှင့် အသံကို စတင်တည်းဖြတ်မည်"):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("အဆင့် 1/4: ဗီဒီယိုနှင့် အသံဖိုင်များကို ဖတ်ရှုနေပါပြီ...")
            progress_bar.progress(20)
            
            clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            status_text.text("အဆင့် 2/4: TikTok AI ရှောင်ရှားရန် ဗီဒီယိုကို ပြုပြင်နေပါပြီ...")
            progress_bar.progress(40)
            
            # မူလ Copyright Effects (Mirror & Resize) + Video Speed 
            effects_list = [
                vfx.MirrorX(), 
                vfx.Resize(width=int(clip.w * 1.05)),
                vfx.MultiplySpeed(video_speed_factor) # ဗီဒီယိုအမြန်နှုန်း အနည်းငယ်တင်ခြင်းဖြင့် AI fingerprint ကို ဖျောက်သည်
            ]
            
            # အရောင်အသွေး အနည်းငယ်ပြောင်းလဲခြင်း (Brightness / Color adjustment)
            if adjust_color:
                # ရုပ်ထွက်အရောင်ကို အနည်းငယ်လင်းစေခြင်း သို့မဟုတ် ချိန်ညှိခြင်း
                effects_list.append(vfx.ColorX(1.05)) # အလင်းအမှောင်/အရောင် အနည်းငယ်စိုစေရန်
            
            clip = clip.with_effects(effects_list)
            
            status_text.text("အဆင့် 3/4: အသံအမြန်နှုန်း ညှိခြင်းနှင့် တစ်ထပ်တည်း ချိန်ကိုက်နေပါပြီ...")
            progress_bar.progress(70)
            
            if speed_factor != 1.0:
                audio_clip = audio_clip.with_effects([vfx.MultiplySpeed(speed_factor)])
            
            if audio_clip.duration < clip.duration:
                clip = clip.subclipped(0, audio_clip.duration)
            else:
                audio_clip = audio_clip.subclipped(0, clip.duration)
            
            final_clip = clip.with_audio(audio_clip)
            
            status_text.text("အဆင့် 4/4: ဗီဒီယိုအသစ်ကို ပေါင်းစပ်ထုတ်လုပ်နေပါပြီ...")
            progress_bar.progress(90)
            
            output_path = "final_output.mp4"
            final_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                fps=24,
                preset="fast"
            )
            
            progress_bar.progress(100)
            status_text.text("✨ တည်းဖြတ်မှု အောင်မြင်ပါပြီ!")
            
            # Telegram Noti ပို့ရန်
            noti_sent = send_telegram_notification("🎬 သင့်ရဲ့ Movie Recap ဗီဒီယို တည်းဖြတ်ပြီးစီးပါပြီ (AI Bypass Version)!")
            if noti_sent:
                st.info("📱 သင့် Telegram ဆီသို့ အကြောင်းကြားစာ (Notification) ပို့ပြီးပါပြီ။")
            
            st.success("သင့်ရဲ့ ဗီဒီယို အသင့်ဖြစ်ပါပြီ။")
            st.video(output_path)
            
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 တည်းဖြတ်ပြီးသား ဗီဒီယိုကို Download ရန်",
                    data=f,
                    file_name="movie_recap_final.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်။")
            st.error(f"မှားယွင်းမှု: {e}")
