import pandas as pd
import random

df = pd.read_csv('creatives_dummy.csv')

# Remove columns if they already exist with // (cleanup)
for col in df.columns:
    if 'Audio //' in col:
        df.drop(columns=[col], inplace=True)

audio_compositions = [
    "Music-driven with sound effects",
    "Voiceover with subtle music and foley",
    "Dialogue-heavy with ambient sound",
    "Minimalist - mostly silence and key sound effects"
]

music_presence = ["Prominent", "Background", "Intermittent", "None"]

music_genres = [
    "Uplifting Pop", "Cinematic Orchestral", "Indie Folk", 
    "Electronic Ambient", "Jazzy", "Ethnic"
]

def get_audio_data():
    comp = random.choice(audio_compositions)
    presence = random.choice(music_presence)
    if presence == "None":
        genre = "N/A"
    else:
        genre = random.choice(music_genres)
    return comp, presence, genre

audio_data = [get_audio_data() for _ in range(len(df))]
df['Audio__Primary Audio Composition'] = [x[0] for x in audio_data]
df['Audio__Music Presence'] = [x[1] for x in audio_data]
df['Audio__Music Genre/Style'] = [x[2] for x in audio_data]

df.to_csv('creatives_dummy.csv', index=False)
print(f"Successfully updated CSV with {len(df)} rows of audio data using __ separator.")
