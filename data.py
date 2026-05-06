import pandas as pd
import csv
import random
import os

# Define possible values based on user description
visual_styles = ["Minimalist", "Cinematic", "Vibrant", "Gritty", "Futuristic", "Documentary-style", "Abstract", "Cartoonish", "Surreal", "Avant-garde", "Retro-futuristic"]
color_palettes = ["Warm tones (reds, oranges)", "Cool tones (blues, greens)", "Monochromatic", "High contrast", "Pastels", "Earthy neutrals", "Bright and saturated", "Neon Glow", "Muted Vintage"]
lighting_styles = ["Natural daylight", "Dramatic/High contrast", "Soft/Diffused", "Bright/Overhead", "Low-key", "High-key", "Colored gels", "Expressive shadows", "Theatrical spotlights"]
talent_types_gen = ["Professional Actor", "Influencer/KOL", "Real Customer/User", "Employee", "Brand Founder/CEO", "Animated/CGI Character", "Animal", "Narrator Only (unseen)", "Mixed", "None"]
demographics = ["Young adult female", "Middle-aged professional male", "Diverse family unit", "Elderly couple", "Children", "Mixed", "Gen Z explorer", "Corporate professional"]
originality = ["Highly Original/Unexpected", "Fresh Take on Familiar", "Standard/Expected", "Clichéd/Uninspired"]
emotional_appeals = ["Aspiration", "Humor", "Empathy", "Nostalgia", "Security", "Empowerment", "Joy", "Fear of Missing Out", "Excitement", "Trust"]
benefits = ["Long-lasting moisture", "Time-saving convenience", "Enhanced connectivity", "Eco-friendly production", "Unbeatable price", "Premium quality", "Instant results", "Healthier lifestyle"]
ctas = ["Purchase now", "Learn more", "Sign up", "Download app", "Follow social media", "Visit store", "Share content", "General brand awareness", "None"]
impact_potential = ["High - likely to provoke discussion/change", "Moderate - raises awareness", "Low - incidental", "None"]
emotional_depth = ["Profound & Evocative", "Moderate & Engaging", "Surface-level/Fleeting", "Purely Functional/None"]
authenticity = ["Highly Authentic/Raw", "Perceived as Real", "Deliberately Stylized Realism", "Clearly Staged/Aspirational", "Fictional/Fantastical"]
hook_messages = ["Introduces a relatable problem", "Presents an intriguing visual", "Poses a direct question", "Showcases a desired outcome", "Displays a startling fact"]
hook_visuals = ["Intriguing/Abstract Visual", "Direct Product Close-up", "Problem Setup Scene", "Shocking/Unexpected Event", "Aspirational Lifestyle Scene", "Facial Close-up of Talent", "Text-heavy Introduction"]
hook_audios = ["Intriguing Sound Effects", "Abrupt Music Start", "Sudden Silence followed by sound", "Upbeat Jingle", "Direct Voiceover Question", "Dialogue snippet", "Whispered confession"]
hook_emotions = ["Curiosity", "Surprise", "Urgency", "Humor", "Empathy", "Confusion", "Anticipation", "Calmness"]
hook_pacing = ["Fast-paced/Rapid Cuts", "Slow/Deliberate", "Static Shot", "Gradual Reveal"]
hook_effectiveness = ["Highly Unique & Effective", "Effective but Standard", "Somewhat Effective/Predictable", "Confusing/Ineffective"]

# Metadata columns from the source CSV
meta_cols = ['link', 'account', 'brand', 'business_unit', 'date_post', 'talent_type', 'is_our_brand', 'views']

# Additional metric columns
extra_cols = ['engagements', 'channels', 'creator type']

generated_headers = [
    "Visuals__Total Video Duration (Seconds)",
    "Visuals__Visual Aesthetic/Style",
    "Visuals__Primary Color Palette",
    "Visuals__Lighting Style",
    "Talent__Main Talent Type",
    "Talent__Number of Key Talent",
    "Talent__Apparent Demographics (Primary)",
    "Messaging__Core Message/Overall Takeaway",
    "Messaging__Message Originality/Uniqueness",
    "Messaging__Primary Emotional Appeal",
    "Messaging__Key Product/Service Benefit Highlighted",
    "Messaging__Call to Action (CTA) Type",
    "Meaningful & Different__Social or Cultural Impact Potential",
    "Meaningful & Different__Emotional Depth",
    "Meaningful & Different__Authenticity & Relatability",
    "Hook__Analyzed Duration (Seconds)",
    "Hook__Primary Message/Question",
    "Hook__Visual Strategy",
    "Hook__Audio Strategy",
    "Hook__On-Screen Text Presence",
    "Hook__Emotional Tone Evoked",
    "Hook__Pacing/Editing (First 3-5s)",
    "Hook__Uniqueness & Effectiveness (Overall)"
]

headers = meta_cols + extra_cols + generated_headers

# Try to load the source CSV for metadata
source_csv = 'creatives_dummy.csv'
if not os.path.exists(source_csv):
    print(f"Warning: {source_csv} not found. Using dummy metadata.")
    metadata = pd.DataFrame([
        ["https://instagram.com/v0", "account1", "Brand A", "Unit 1", "2024-01-01", "Mikro", "True", 500000]
    ] * 50, columns=meta_cols)
else:
    df_source = pd.read_csv(source_csv)
    # Ensure columns exist in source
    metadata = df_source[meta_cols]

rows = []
for _, meta_row in metadata.iterrows():
    # 1. Generate additional metrics
    views_val = meta_row['views']
    engagements = int(views_val * random.uniform(0.01, 0.05)) # 1-5% engagement rate
    channels = "instagram"
    creator_type = random.choice(["brand say", "other say"])
    
    extra_data = [engagements, channels, creator_type]

    # 2. Generate analysis data
    duration = random.randint(15, 60)
    talent_type_gen_val = random.choice(talent_types_gen)
    num_talent = "0" if talent_type_gen_val in ["Narrator Only (unseen)", "None"] else str(random.choice([1, 2, 3, "5+"]))
    
    # Generate messaging content
    benefit = random.choice(benefits)
    message = f"Experience the power of {benefit.lower()} with our latest innovation."
    
    # Meaningful impact with brief description
    impact = random.choice(impact_potential)
    if impact != "None":
        impact += f" - {random.choice(['Challenges gender norms', 'Focuses on sustainability', 'Promotes inclusivity'])}"
        
    # Hook text presence
    text_presence = random.choice(["Yes", "No"])
    if text_presence == "Yes":
        text_presence += f" - '{random.choice(['Stop!', 'Wait...', 'Limited Offer', 'How to?', 'The Secret'])}'"

    generated_data = [
        duration,
        random.choice(visual_styles),
        random.choice(color_palettes),
        random.choice(lighting_styles),
        talent_type_gen_val,
        num_talent,
        random.choice(demographics) if talent_type_gen_val not in ["Narrator Only (unseen)", "None", "Animal"] else "N/A",
        message,
        random.choice(originality),
        random.choice(emotional_appeals),
        benefit,
        random.choice(ctas),
        impact,
        random.choice(emotional_depth),
        random.choice(authenticity),
        random.randint(3, 5),
        random.choice(hook_messages),
        random.choice(hook_visuals),
        random.choice(hook_audios),
        text_presence,
        random.choice(hook_emotions),
        random.choice(hook_pacing),
        random.choice(hook_effectiveness)
    ]
    
    row = list(meta_row) + extra_data + generated_data
    rows.append(row)

with open('dummy_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"CSV generated successfully with {len(rows)} rows and updated columns.")
