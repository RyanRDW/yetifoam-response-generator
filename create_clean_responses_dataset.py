#!/usr/bin/env python3
"""
Create clean responses dataset from corrupted Yetifoam data
Extracts individual Q&A pairs and removes instruction/transcript text
"""

import json
import pandas as pd
import re
from typing import List, Dict, Any
import os

def load_json_dataset(file_path: str) -> List[Dict]:
    """Load JSON dataset"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'items' in data:
        return data['items']
    return data

def extract_individual_responses(large_text: str) -> List[Dict[str, str]]:
    """Extract individual response sections from large document text"""
    responses = []
    
    # Split by section patterns
    sections = re.split(r'\n(?=\d+\.\d+\s+|\w+\s+–\s+)', large_text)
    
    for section in sections:
        section = section.strip()
        if len(section) < 50:  # Skip very short sections
            continue
            
        # Skip document headers and meta text
        if any(skip_phrase in section.lower() for skip_phrase in [
            'make sure to include',
            'markers to provide citations',
            'below is a reconstructed',
            'transcript',
            'customer:',
            'ryan:',
            'yetifoam social media comment responses',
            'this document summarises',
            'this updated document',
            'each response has been organised'
        ]):
            continue
        
        # Extract individual response items
        if '–' in section:
            # Split on response patterns like "Topic – Response text"
            parts = section.split('–', 1)
            if len(parts) == 2:
                topic = parts[0].strip()
                response = parts[1].strip()
                
                # Clean the topic
                topic = re.sub(r'^\d+\.\d*\s*', '', topic)
                topic = re.sub(r'^•\s*', '', topic)
                
                # Clean the response
                response = clean_response_text(response)
                
                if len(response) > 50 and is_valid_response(response):
                    responses.append({
                        'topic': topic,
                        'response': response,
                        'category': extract_category_from_topic(topic)
                    })
    
    return responses

def clean_response_text(text: str) -> str:
    """Clean response text for social media use"""
    if not text:
        return ""
    
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Remove section markers and bullets
    text = re.sub(r'^\d+\.\d*\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^•\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\-\s*', '', text, flags=re.MULTILINE)
    
    # Convert instructional language to direct
    replacements = {
        'Encourage commenters to': 'We recommend you',
        'Advise commenters that': 'We suggest',
        'Explain that': '',
        'Clarify that': '',
        'Reassure commenters that': 'Rest assured',
        'Emphasise that': 'It\'s important to know that'
    }
    
    for old, new in replacements.items():
        text = re.sub(old, new, text, flags=re.IGNORECASE)
    
    # Clean up spacing
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def is_valid_response(text: str) -> bool:
    """Check if text is a valid response (not instruction/transcript text)"""
    text_lower = text.lower()
    
    # Skip if contains instruction markers
    invalid_patterns = [
        'make sure to include',
        'markers to provide citations', 
        'below is a reconstructed',
        'transcript',
        'customer:',
        'ryan:',
        'call script',
        '**yetifoam social media',
        'this document',
        'language model'
    ]
    
    if any(pattern in text_lower for pattern in invalid_patterns):
        return False
    
    # Must contain actual product/service information
    valid_patterns = [
        'yetifoam',
        'spray foam',
        'insulation',
        'r-value',
        'moisture',
        'thermal',
        'polyurethane',
        'installation'
    ]
    
    if not any(pattern in text_lower for pattern in valid_patterns):
        return False
    
    return True

def extract_category_from_topic(topic: str) -> str:
    """Extract category from topic text"""
    topic_lower = topic.lower()
    
    if any(word in topic_lower for word in ['moisture', 'condensation', 'damp', 'water', 'vapour']):
        return 'Moisture Resistance'
    elif any(word in topic_lower for word in ['r-value', 'thermal', 'performance', 'energy', 'efficiency']):
        return 'Thermal Performance' 
    elif any(word in topic_lower for word in ['fire', 'safety', 'compliance', 'standard']):
        return 'Fire Safety & Compliance'
    elif any(word in topic_lower for word in ['electrical', 'wiring', 'cable', 'electric']):
        return 'Electrical Safety'
    elif any(word in topic_lower for word in ['price', 'cost', 'quote', 'pricing']):
        return 'Pricing & Cost'
    elif any(word in topic_lower for word in ['installation', 'install', 'clearance', 'access']):
        return 'Installation & Application'
    elif any(word in topic_lower for word in ['contact', 'quote', 'enquiry', 'service']):
        return 'General Information & Contact'
    else:
        return 'General Information'

def main():
    """Create clean responses dataset"""
    print("🔧 CLEANING YETIFOAM DATASET - REMOVING CORRUPTED ENTRIES")
    print("=" * 60)
    
    # Load current corrupted dataset
    dataset_path = "YETIFOAM_COVERAGE_OPTIMIZED_v5.json"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset file not found: {dataset_path}")
        return
    
    print(f"📂 Loading dataset: {dataset_path}")
    raw_data = load_json_dataset(dataset_path)
    print(f"📊 Raw items loaded: {len(raw_data)}")
    
    # Extract clean individual responses
    all_clean_responses = []
    
    print("\n🧹 Extracting clean individual responses...")
    
    for i, item in enumerate(raw_data[:50]):  # Process first 50 items to start
        print(f"Processing item {i+1}/50", end='\r')
        
        # Get response text from various fields
        text_sources = []
        for field in ['standardized_response', 'response_text', 'original_text']:
            if field in item and item[field]:
                text_sources.append(item[field])
        
        # Extract responses from each text source
        for text in text_sources:
            individual_responses = extract_individual_responses(text)
            
            # Add metadata from original item
            for response in individual_responses:
                response['source'] = item.get('source', 'Unknown')
                response['original_category'] = item.get('category', 'Unknown')
                all_clean_responses.append(response)
    
    print(f"\n✅ Extracted {len(all_clean_responses)} clean responses")
    
    # Remove duplicates based on response text
    print("\n🔄 Removing duplicates...")
    unique_responses = []
    seen_responses = set()
    
    for response in all_clean_responses:
        # Create a signature for duplicate detection
        signature = response['response'][:100].lower().strip()
        
        if signature not in seen_responses:
            seen_responses.add(signature)
            unique_responses.append(response)
    
    print(f"✅ Final clean responses: {len(unique_responses)}")
    
    # Create DataFrame and save as parquet
    print("\n💾 Creating parquet file...")
    df = pd.DataFrame(unique_responses)
    
    # Display sample of what we're saving
    print("\n📋 SAMPLE CLEAN RESPONSES:")
    print("-" * 60)
    for i, response in enumerate(unique_responses[:3]):
        print(f"Response {i+1}:")
        print(f"Topic: {response['topic']}")
        print(f"Category: {response['category']}")
        print(f"Response: {response['response'][:200]}...")
        print("-" * 40)
    
    # Save as parquet
    parquet_path = "responses_dataset.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"✅ Saved clean dataset: {parquet_path}")
    
    # Also save as JSON for backup
    json_path = "responses_dataset_clean.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(unique_responses, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved JSON backup: {json_path}")
    
    print(f"\n🎉 DATASET CLEANING COMPLETED!")
    print(f"📊 Original corrupted items: {len(raw_data)}")
    print(f"📊 Clean individual responses: {len(unique_responses)}")
    print(f"📁 Files created: {parquet_path}, {json_path}")
    
    # Show category breakdown
    category_counts = pd.Series([r['category'] for r in unique_responses]).value_counts()
    print(f"\n📈 CATEGORY BREAKDOWN:")
    for category, count in category_counts.items():
        print(f"  {category}: {count} responses")

if __name__ == "__main__":
    main()