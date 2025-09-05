#!/usr/bin/env python3
"""
Clean corrupted dataset entries from responses_dataset.parquet
"""
import pandas as pd
import re

def clean_dataset():
    # Load main dataset
    df = pd.read_parquet('responses_dataset.parquet')
    print('Original dataset shape:', df.shape)
    print('Original columns:', list(df.columns))

    # Identify corrupted responses
    corrupted_indices = []
    corrupted_examples = []

    for i, row in df.iterrows():
        response = str(row['response'])
        topic = str(row['topic'])
        
        # Corruption criteria
        is_corrupted = False
        corruption_reasons = []
        
        if len(response) > 3000:  # Excessive length
            is_corrupted = True
            corruption_reasons.append('excessive_length')
        
        if 'DOCS_modelChunk' in response or 'DOCS_modelChunk' in topic:
            is_corrupted = True
            corruption_reasons.append('parsing_artifacts')
        
        if r'\u' in response or response.count(r'\n') > 3:
            is_corrupted = True
            corruption_reasons.append('unicode_issues')
        
        if 'Meta Comment Responses' in topic or 'Meta Comment' in response:
            is_corrupted = True
            corruption_reasons.append('meta_responses')
        
        if len(topic.split()) > 50:  # Topic too long
            is_corrupted = True
            corruption_reasons.append('corrupted_topic')
        
        if is_corrupted:
            corrupted_indices.append(i)
            if len(corrupted_examples) < 3:
                corrupted_examples.append({
                    'index': i,
                    'topic_preview': topic[:100],
                    'response_preview': response[:200],
                    'reasons': corruption_reasons,
                    'length': len(response),
                    'original_topic': topic,
                    'original_response': response
                })

    print(f'Found {len(corrupted_indices)} corrupted responses at indices:', corrupted_indices)

    # Show corruption examples
    for i, example in enumerate(corrupted_examples):
        print(f'\nCorrupted Example {i+1}:')
        print(f'  Index: {example["index"]}')
        print(f'  Topic: {example["topic_preview"]}...')
        print(f'  Response length: {example["length"]}')
        print(f'  Corruption reasons: {example["reasons"]}')
        print(f'  Response preview: {example["response_preview"]}...')

    # Clean dataset by removing corrupted entries
    clean_df = df.drop(index=corrupted_indices).reset_index(drop=True)

    # Save cleaned dataset
    clean_df.to_parquet('cleaned_responses_dataset.parquet')

    print(f'\nCleaned dataset shape: {clean_df.shape}')
    print(f'Removed {len(corrupted_indices)} corrupted responses')
    print(f'Retained {len(clean_df)} clean responses')

    # Show examples of clean responses
    print('\nClean Response Examples:')
    for i in range(min(3, len(clean_df))):
        print(f'\nClean Example {i+1}:')
        print(f'  Topic: {clean_df.iloc[i]["topic"]}')
        print(f'  Response: {clean_df.iloc[i]["response"][:300]}...')

    return corrupted_examples, clean_df

if __name__ == "__main__":
    clean_dataset()