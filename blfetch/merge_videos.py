import os
import json
import subprocess

# --- User settings ---
video_folder = "./videos"
subs_folder = "./subs"
output_video = "combined.mp4"
output_subs = "combined.ass"

# --- Step 1: Collect video and subtitle files ---
videos = sorted([os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(('.mp4', '.mkv'))])
subs = sorted([os.path.join(subs_folder, f) for f in os.listdir(subs_folder) if f.endswith('.ass')])
input(videos)
# --- Step 2: Merge all ASS files properly (keep only first header) ---
def merge_ass_files(sub_files, output):
    header = []
    events = []
    header_done = False

    for idx, path in enumerate(sub_files):
        with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            lines = f.readlines()

        in_events = False
        for line in lines:
            if line.strip().startswith("[Events]"):
                in_events = True
                if not header_done:
                    header.append(line)
                continue

            if in_events:
                # Only append dialogues
                if line.strip().startswith("Dialogue:"):
                    events.append(line)
            else:
                # Before [Events], keep header only for first file
                if not header_done:
                    header.append(line)

        header_done = True  # header copied from first file only

    with open(output, 'w', encoding='utf-8-sig', errors='ignore') as f:
        f.writelines(header + events)

    print(f"✅ Combined subtitles into {output}")

merge_ass_files(subs, output_subs)

# --- Step 3: Create FFmpeg concat list file ---
list_file = "concat_list.txt"
with open(list_file, "w", encoding="utf-8") as f:
    for v in videos:
        f.write(f"file '{os.path.abspath(v)}'\n")

print(f"✅ Created {list_file} with {len(videos)} clips")

# --- Step 4: Check codec consistency ---
def get_codec_info(file):
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'json', file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data['streams'][0]['codec_name']
    except Exception:
        return None

codecs = [get_codec_info(v) for v in videos if get_codec_info(v)]
print(set(codecs))
same_codec = len(set(codecs)) == 1

# --- Step 5: Merge videos (try copy, fallback to re-encode) ---
if same_codec:
    print("🎬 All clips share same codec. Merging without transcoding...")
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file,
        "-c", "copy", "-y", output_video
    ]
else:
    print("⚠️ Codecs differ. Merging with transcoding...")
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:v", "libx264", "-c:a", "aac", "-preset", "veryfast", "-crf", "18", "-y", output_video
    ]

subprocess.run(cmd, check=True)
print(f"✅ Combined video saved as {output_video}")

# --- Step 6: Burn the merged ASS into video ---
final_output = "final_with_subs.mp4"
cmd = [
    "ffmpeg", "-i", output_video, "-vf", f"ass={output_subs}",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "aac", "-y", final_output
]
subprocess.run(cmd, check=True)

print(f"🎉 Final video with subtitles saved as {final_output}")
