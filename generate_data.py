import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_dummy_data(num_rows=1000):
    brands = {
        "Beauty and Wellbeing": {
            "our": ["Dove", "Sunsilk", "Vaseline", "Lux", "Pond's", "TRESemmé"],
            "competitor": ["Wardah", "Scarlett", "Biore", "Pantene", "Make Over"]
        },
        "Home Care": {
            "our": ["Sunlight", "Rinso", "Molto", "Wipol", "Super Pell"],
            "competitor": ["Mama Lemon", "So Klin", "Attack", "Downy", "Vanish"]
        }
    }

    talent_types = ["Mega", "Makro", "Mikro", "Nano"]
    emotions = ["happy", "surprised", "neutral", "sad", "angry"]
    sentiments = ["excited", "calm", "neutral", "energetic", "serious"]
    topics = {
        "Beauty and Wellbeing": ["skincare", "haircare", "makeup", "fragrance", "wellness"],
        "Home Care": ["cleaning hacks", "laundry tips", "dishwashing", "home fragrance", "disinfecting"]
    }
    formats = ["storytelling", "tutorial", "reaction", "before after", "talking head", "vlog", "aesthetic"]
    tones = ["funny", "serious", "emotional", "inspirational", "dramatic", "calm"]
    hook_types = ["question", "shocking statement", "relatable statement", "curiosity gap", "visual hook"]

    data = []
    start_date = datetime(2024, 1, 1)

    for i in range(num_rows):
        bu = random.choice(list(brands.keys()))
        is_our = random.random() > 0.4
        brand_list = brands[bu]["our"] if is_our else brands[bu]["competitor"]
        brand = random.choice(brand_list)
        
        # Numerical values with some logic
        views = int(np.random.lognormal(mean=13, sigma=1)) # Typical social media distribution
        duration = random.randint(5, 60)
        face_present = random.choices([0, 1, 2, 3], weights=[0.2, 0.5, 0.2, 0.1])[0]
        
        face_emotion = random.choice(emotions) if face_present > 0 else None
        text_overlay = random.randint(0, 10)
        scene_cuts = random.randint(2, 20)
        speech_ratio = round(random.uniform(0, 1), 2)
        voice_sentiment = random.choice(sentiments) if speech_ratio > 0.1 else None
        
        topic = random.choice(topics[bu])
        content_format = random.choice(formats)
        tone = random.choice(tones)
        
        hook_present = random.random() > 0.2
        hook_duration = random.randint(1, 5) if hook_present else None
        hook_type = random.choice(hook_types) if hook_present else None
        
        word_density = round(random.uniform(1.5, 4.0), 2) if speech_ratio > 0.5 else None
        
        date_post = start_date + timedelta(days=random.randint(0, 200))

        data.append({
            "link": f"https://tiktok.com/v{i}",
            "account": f"{brand.lower().replace(' ', '_')}_official",
            "brand": brand,
            "business_unit": bu,
            "date_post": date_post.strftime('%Y-%m-%d'),
            "talent_type": random.choice(talent_types),
            "is_our_brand": is_our,
            "views": views,
            "duration_sec": duration,
            "face_present": face_present,
            "face_emotion": face_emotion,
            "text_overlay_count": text_overlay,
            "scene_cut_estimate": scene_cuts,
            "speech_ratio": speech_ratio,
            "voice_sentiment": voice_sentiment,
            "topic": topic,
            "format": content_format,
            "tone": tone,
            "hook_present": hook_present,
            "hook_duration_sec": hook_duration,
            "hook_type": hook_type,
            "word_density_wps": word_density
        })

    df = pd.DataFrame(data)
    df.to_csv("creatives_dummy.csv", index=False)
    print(f"Generated {num_rows} rows of dummy data in creatives_dummy.csv")

if __name__ == "__main__":
    generate_dummy_data(1000)
