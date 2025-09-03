#!/usr/bin/env python3
"""
Dataset cleaner for Yetifoam Response Generator
Analyzes, cleans, validates, and rebuilds corrupted Parquet dataset
"""

import pandas as pd
import re
import json
import sys
from typing import List, Tuple, Dict, Any

def load_dataset(file_path: str) -> pd.DataFrame:
    """Load the corrupted dataset and print initial stats"""
    try:
        df = pd.read_parquet(file_path)
        print(f"✓ Dataset loaded successfully")
        print(f"✓ Row count: {len(df)}")
        print(f"✓ Column names: {list(df.columns)}")
        print(f"✓ Sample of first 5 rows:")
        print(df.head().to_string())
        return df
    except Exception as e:
        print(f"✗ Error loading dataset: {e}")
        sys.exit(1)

def analyze_corruption_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze data for corruption patterns"""
    print("\n=== ANALYZING CORRUPTION PATTERNS ===")
    
    corruption_patterns = {
        'metadata_instructions': r'Make sure to include\s*``\s*markers|provide citations|Formatting instructions|format the response|include citations',
        'call_transcripts': r'Customer:\s*\(Calling in\)|Hi, is this Ryan|Ryan:\s*|Customer Service|phone call',
        'document_headers': r'\*\*Yetifoam Social Media Comment Responses\s*[–-]\s*Categorised\s*\(Updated\)\*\*|\*\*Category:\s*\w+\*\*',
        'partial_urls_dates': r'https?://[^\s]*\s*(incomplete)|^\d{4}-\d{2}-\d{2}|Updated on \d+',
        'truncated_sentences': 'SPECIAL_CHECK',  # Will be handled separately
        'mixed_metadata': r'\[Metadata:\s*.*?\]|\{Document ID:\s*\w+\}|Document ID|Metadata'
    }
    
    # Add corruption analysis columns
    df['is_corrupted'] = False
    df['corruption_types'] = [[] for _ in range(len(df))]
    
    # Determine the text column to analyze
    text_column = None
    possible_text_columns = ['text', 'response', 'content', 'question', 'answer']
    for col in possible_text_columns:
        if col in df.columns:
            text_column = col
            break
    
    if text_column is None:
        # Use first string column
        for col in df.columns:
            if df[col].dtype == 'object':
                text_column = col
                break
    
    print(f"✓ Using column '{text_column}' for corruption analysis")
    
    corruption_stats = {}
    
    for idx, row in df.iterrows():
        text = str(row[text_column]) if pd.notna(row[text_column]) else ""
        row_corruption_types = []
        
        # Check each pattern
        for pattern_name, pattern in corruption_patterns.items():
            if pattern_name == 'truncated_sentences':
                # Check if text ends mid-word (no punctuation and last word is very short)
                if text and not re.search(r'[.!?]\s*$', text.strip()):
                    words = text.split()
                    if words and len(words[-1]) < 3:
                        row_corruption_types.append(pattern_name)
            else:
                if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                    row_corruption_types.append(pattern_name)
        
        # Update DataFrame
        if row_corruption_types:
            df.at[idx, 'is_corrupted'] = True
            df.at[idx, 'corruption_types'] = row_corruption_types
            
        # Update stats
        for corruption_type in row_corruption_types:
            corruption_stats[corruption_type] = corruption_stats.get(corruption_type, 0) + 1
    
    # Generate summary report
    total_rows = len(df)
    corrupted_rows = df['is_corrupted'].sum()
    clean_rows = total_rows - corrupted_rows
    
    print(f"\n=== CORRUPTION ANALYSIS REPORT ===")
    print(f"Total rows: {total_rows}")
    print(f"Corrupted rows: {corrupted_rows} ({corrupted_rows/total_rows*100:.1f}%)")
    print(f"Clean rows: {clean_rows} ({clean_rows/total_rows*100:.1f}%)")
    print(f"\nCorruption types found:")
    for corruption_type, count in corruption_stats.items():
        print(f"  {corruption_type}: {count} rows")
    
    # Show examples
    print(f"\n=== EXAMPLES ===")
    if corrupted_rows > 0:
        print("Example corrupted entries:")
        corrupted_sample = df[df['is_corrupted']].head(2)
        for idx, row in corrupted_sample.iterrows():
            print(f"Row {idx} (types: {row['corruption_types']}):")
            print(f"  {str(row[text_column])[:200]}...")
            print()
    
    if clean_rows > 0:
        print("Example clean entries:")
        clean_sample = df[~df['is_corrupted']].head(2)
        for idx, row in clean_sample.iterrows():
            print(f"Row {idx}:")
            print(f"  {str(row[text_column])[:200]}...")
            print()
    
    return df

def extract_qa_pairs(text: str) -> Tuple[str, str]:
    """Extract question and answer from text"""
    if not text or pd.isna(text):
        return "", ""
    
    text = str(text).strip()
    
    # Try different Q&A delimiters
    qa_patterns = [
        r'Q:\s*(.*?)\s*A:\s*(.*)',
        r'Question:\s*(.*?)\s*Answer:\s*(.*)',
        r'^(.*?\?)\s*(.*)',  # Text ending with ? followed by response
    ]
    
    for pattern in qa_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            question = match.group(1).strip()
            answer = match.group(2).strip()
            if question and answer:
                return question, answer
    
    # If no clear Q&A structure, check if it starts with a question
    sentences = re.split(r'[.!?]+', text)
    if sentences and sentences[0].strip().endswith('?'):
        question = sentences[0].strip()
        answer = ' '.join(sentences[1:]).strip()
        if answer:
            return question, answer
    
    # Default: treat entire text as response with empty question
    return "", text

def clean_text(text: str) -> str:
    """Clean corruption from text"""
    if not text or pd.isna(text):
        return ""
    
    text = str(text)
    
    # Remove corruption patterns
    corruption_patterns = [
        r'Make sure to include\s*``\s*markers.*?(?=\n\n|\Z)',
        r'provide citations.*?(?=\n\n|\Z)',
        r'Formatting instructions.*?(?=\n\n|\Z)',
        r'Customer:\s*\(Calling in\).*?Ryan:\s*',
        r'Hi, is this Ryan.*?(?=\n\n|\Z)',
        r'\*\*Yetifoam Social Media Comment Responses\s*[–-]\s*Categorised\s*\(Updated\)\*\*',
        r'\*\*Category:\s*\w+\*\*',
        r'https?://[^\s]*\s*\(incomplete\)',
        r'Updated on \d+.*?(?=\n\n|\Z)',
        r'\[Metadata:\s*.*?\]',
        r'\{Document ID:\s*\w+\}',
        r'Document ID:.*?(?=\n\n|\Z)',
    ]
    
    for pattern in corruption_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'#{1,6}\s*', '', text)         # Headers
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines
    text = re.sub(r'\s{2,}', ' ', text)     # Multiple spaces
    text = text.strip()
    
    # Remove incomplete sentences at the end
    if text and not re.search(r'[.!?]\s*$', text):
        # Find last complete sentence
        sentences = re.split(r'([.!?]+)', text)
        if len(sentences) > 2:
            # Keep everything up to the last punctuation
            complete_text = ''.join(sentences[:-1])
            if len(complete_text.strip()) > 50:
                text = complete_text.strip()
    
    return text

def infer_category(text: str) -> str:
    """Infer category from text content"""
    if not text:
        return "Uncategorized"
    
    text_lower = text.lower()
    
    category_keywords = {
        'Product Information': ['product', 'spray foam', 'insulation', 'r-value', 'thickness'],
        'Installation': ['install', 'application', 'how to apply', 'preparation', 'surface'],
        'Technical Support': ['problem', 'issue', 'troubleshoot', 'not working', 'failed'],
        'Pricing': ['cost', 'price', 'expensive', 'cheap', 'budget', 'quote'],
        'Safety': ['safe', 'toxic', 'ventilation', 'protection', 'health'],
        'Comparison': ['vs', 'versus', 'compare', 'difference', 'better than'],
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return "General"

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataset and extract valid Q&A pairs"""
    print("\n=== CLEANING DATASET ===")
    
    # Determine text column
    text_column = None
    possible_text_columns = ['text', 'response', 'content', 'question', 'answer']
    for col in possible_text_columns:
        if col in df.columns:
            text_column = col
            break
    
    if text_column is None:
        for col in df.columns:
            if df[col].dtype == 'object':
                text_column = col
                break
    
    clean_data = []
    discarded_count = 0
    
    for idx, row in df.iterrows():
        text = str(row[text_column]) if pd.notna(row[text_column]) else ""
        
        # Skip if heavily corrupted (>50% corruption indicators)
        corruption_indicators = len(row['corruption_types']) if 'corruption_types' in row else 0
        if corruption_indicators > 2:  # Too many corruption types
            discarded_count += 1
            continue
        
        # Clean the text
        cleaned_text = clean_text(text)
        if len(cleaned_text) < 50:  # Too short after cleaning
            discarded_count += 1
            continue
        
        # Extract Q&A pairs
        question, answer = extract_qa_pairs(cleaned_text)
        
        # If no clear Q&A structure, treat as response with inferred question
        if not question and answer:
            # Try to infer question type from response
            if 'how' in answer.lower()[:100]:
                question = "How does this work?"
            elif 'what' in answer.lower()[:100]:
                question = "What is this about?"
            elif 'spray foam' in answer.lower():
                question = "Tell me about spray foam."
            else:
                question = "Can you provide information?"
            
        if not answer:
            answer = cleaned_text
        
        # Final validation
        if len(answer) < 100:  # Response too short
            discarded_count += 1
            continue
        
        # Check for remaining corruption in the answer
        corruption_check = re.search(
            r'Make sure to include|provide citations|Customer:|Document ID|Metadata',
            answer, re.IGNORECASE
        )
        if corruption_check:
            discarded_count += 1
            continue
        
        clean_data.append({
            'question': question,
            'response': answer,
            'category': infer_category(answer),
            'original_row_id': idx
        })
    
    print(f"✓ Processed {len(df)} original rows")
    print(f"✓ Created {len(clean_data)} clean entries")
    print(f"✓ Discarded {discarded_count} corrupted entries")
    
    return pd.DataFrame(clean_data)

def calculate_quality_score(response: str) -> float:
    """Calculate quality score for a response"""
    if not response:
        return 0.0
    
    score = 0.0
    
    # Length component (normalized to 0-1, capped at 500 chars)
    length_score = min(len(response) / 500, 1.0)
    score += length_score * 0.4
    
    # Completeness (ends with proper punctuation)
    if re.search(r'[.!?]\s*$', response.strip()):
        score += 0.3
    
    # Coherence (has multiple sentences)
    sentence_count = len(re.findall(r'[.!?]+', response))
    if sentence_count >= 2:
        score += 0.2
    
    # Information density (not too repetitive)
    words = response.lower().split()
    if words:
        unique_word_ratio = len(set(words)) / len(words)
        score += unique_word_ratio * 0.1
    
    return min(score, 1.0)

def validate_and_rebuild_dataset(clean_df: pd.DataFrame) -> pd.DataFrame:
    """Validate and add quality scoring to the cleaned dataset"""
    print("\n=== VALIDATING AND REBUILDING DATASET ===")
    
    # Add quality scores
    clean_df['quality_score'] = clean_df['response'].apply(calculate_quality_score)
    
    # Validate each entry
    valid_mask = (
        (clean_df['response'].str.len() >= 100) &  # Minimum length
        (clean_df['quality_score'] >= 0.5) &       # Minimum quality
        (~clean_df['response'].str.contains(
            r'Make sure to include|provide citations|Customer:|Document ID|Metadata',
            case=False, regex=True, na=False
        ))  # No remaining corruption
    )
    
    validated_df = clean_df[valid_mask].copy()
    discarded_validation = len(clean_df) - len(validated_df)
    
    print(f"✓ Validated dataset: {len(validated_df)} rows")
    print(f"✓ Discarded in validation: {discarded_validation} rows")
    print(f"✓ Quality score range: {validated_df['quality_score'].min():.2f} - {validated_df['quality_score'].max():.2f}")
    print(f"✓ Average quality score: {validated_df['quality_score'].mean():.2f}")
    
    # Category distribution
    print(f"\n✓ Category distribution:")
    category_counts = validated_df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count}")
    
    return validated_df

def main():
    """Main execution function"""
    print("=== YETIFOAM DATASET CLEANER ===")
    
    # Load dataset
    df = load_dataset('responses_dataset.parquet')
    
    # Analyze corruption
    df = analyze_corruption_patterns(df)
    
    # Clean dataset
    clean_df = clean_dataset(df)
    
    # Validate and rebuild
    final_df = validate_and_rebuild_dataset(clean_df)
    
    # Save cleaned dataset
    output_file = 'clean_responses_dataset.parquet'
    final_df.to_parquet(output_file, index=False)
    print(f"\n✓ Saved cleaned dataset to: {output_file}")
    
    # Show sample of final data
    print(f"\n=== SAMPLE OF CLEAN DATA ===")
    print(final_df[['question', 'response', 'category', 'quality_score']].head().to_string())
    
    print(f"\n🎉 SUCCESS: Cleaned dataset contains {len(final_df)} high-quality Q&A pairs")
    
    return final_df

if __name__ == "__main__":
    main()