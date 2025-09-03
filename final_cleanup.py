#!/usr/bin/env python3
"""
Final cleanup script for remaining corruption in clean dataset
"""

import pandas as pd
import re

def advanced_clean_text(text):
    """Remove all remaining corruption patterns"""
    if not text or pd.isna(text):
        return ""
    
    text = str(text)
    
    # Remove UUID patterns
    text = re.sub(r'strVe?ndorUUID[=\\u003d]+[a-f0-9-]+[a-f0-9-]*', '', text, flags=re.IGNORECASE)
    
    # Remove binary/encoded content
    text = re.sub(r'\\u[0-9a-f]{4}', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\\n\\n\\u[0-9a-f]{4}', '', text, flags=re.IGNORECASE)
    
    # Remove ServiceM8 booking URLs
    text = re.sub(r'https://book\.servicem8\.com/[^\s]*', '', text, flags=re.IGNORECASE)
    
    # Remove date patterns that look corrupted
    text = re.sub(r'\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2}', '', text)
    
    # Remove document references
    text = re.sub(r'Yetifoam Meta Comment Responses - Google Docs', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https://docs\.google\.com/[^\s]*', '', text)
    
    # Remove control characters and weird spacing
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # If text starts with incomplete words or fragments, try to find the real start
    sentences = text.split('. ')
    if len(sentences) > 1:
        # Look for the first sentence that looks like a proper start
        for i, sentence in enumerate(sentences):
            if len(sentence) > 20 and sentence[0].isupper() and not re.match(r'^[a-z\s]{1,10}[A-Z]', sentence):
                text = '. '.join(sentences[i:])
                break
    
    return text

def main():
    # Load the current clean dataset
    df = pd.read_parquet('clean_responses_dataset.parquet')
    print(f"Loaded {len(df)} records")
    
    # Apply advanced cleaning
    print("Applying advanced cleaning...")
    df['response'] = df['response'].apply(advanced_clean_text)
    
    # Remove entries that are now too short or still corrupted
    valid_mask = (
        (df['response'].str.len() >= 50) &
        (~df['response'].str.contains(r'UUID', case=False, na=False)) &
        (~df['response'].str.contains(r'strVe', case=False, na=False)) &
        (~df['response'].str.startswith('strVendorUUID', na=False))
    )
    
    original_count = len(df)
    df_clean = df[valid_mask].copy()
    removed_count = original_count - len(df_clean)
    
    print(f"Removed {removed_count} corrupted entries")
    print(f"Final clean dataset: {len(df_clean)} records")
    
    # Save the final clean dataset
    df_clean.to_parquet('clean_responses_dataset.parquet', index=False)
    print("✅ Saved final clean dataset")
    
    # Show sample of cleaned data
    print("\n=== SAMPLE OF FINAL CLEAN DATA ===")
    for i in range(min(3, len(df_clean))):
        response = df_clean.iloc[i]['response']
        print(f"\nResponse {i+1} ({len(response)} chars):")
        print(response[:200] + "..." if len(response) > 200 else response)

if __name__ == "__main__":
    main()