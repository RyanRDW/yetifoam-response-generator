#!/usr/bin/env python3
"""
Reconcile multiple dataset versions into a unified schema
"""
import pandas as pd
import numpy as np

def reconcile_datasets():
    # Load all datasets
    print("Loading datasets...")
    
    # Cleaned main dataset (51 rows)
    cleaned_df = pd.read_parquet('cleaned_responses_dataset.parquet')
    print(f"Cleaned dataset: {cleaned_df.shape}, columns: {list(cleaned_df.columns)}")
    
    # Original clean dataset (12 rows) 
    try:
        clean_df = pd.read_parquet('clean_responses_dataset.parquet')
        print(f"Clean dataset: {clean_df.shape}, columns: {list(clean_df.columns)}")
    except Exception as e:
        print(f"Error loading clean dataset: {e}")
        clean_df = pd.DataFrame()
    
    # Unified dataset (67 rows)
    try:
        unified_df = pd.read_parquet('unified_responses.parquet')
        print(f"Unified dataset: {unified_df.shape}, columns: {list(unified_df.columns)}")
    except Exception as e:
        print(f"Error loading unified dataset: {e}")
        unified_df = pd.DataFrame()
    
    # Convert cleaned_df to target schema
    final_rows = []
    
    for _, row in cleaned_df.iterrows():
        topic = str(row['topic']).strip()
        response = str(row['response']).strip()
        category = str(row['category']).strip()
        
        # Parse topic into category/subcategory
        if '\n' in topic:
            lines = topic.split('\n')
            main_topic = lines[0].strip()
            subcategory = lines[1].strip() if len(lines) > 1 else ""
        else:
            main_topic = topic
            subcategory = ""
        
        # Extract context keywords from topic and response
        context_keywords = []
        if main_topic:
            context_keywords.extend(main_topic.lower().split())
        if subcategory:
            context_keywords.extend(subcategory.lower().split())
        
        # Clean and format keywords
        context_keywords = [w for w in context_keywords if len(w) > 2]
        context_keywords = list(set(context_keywords[:10]))  # Limit and dedupe
        
        final_rows.append({
            'category': category if category and category != 'nan' else main_topic,
            'subcategory': subcategory,
            'context_keywords': ', '.join(context_keywords),
            'answer': response,
            'notes': f"Source: {row.get('source', 'responses_dataset')}"
        })
    
    # Add unique entries from clean_df if available
    if not clean_df.empty and 'question' in clean_df.columns:
        for _, row in clean_df.iterrows():
            question = str(row['question']).strip()
            answer = str(row['response']).strip()
            category = str(row['category']).strip()
            
            # Check if this response already exists
            duplicate = False
            for existing in final_rows:
                if answer.lower() in existing['answer'].lower() or existing['answer'].lower() in answer.lower():
                    duplicate = True
                    break
            
            if not duplicate:
                final_rows.append({
                    'category': category,
                    'subcategory': question,
                    'context_keywords': ', '.join(question.lower().split()[:10]),
                    'answer': answer,
                    'notes': f"Source: clean_responses_dataset, Quality: {row.get('quality_score', 'N/A')}"
                })
    
    # Add unique entries from unified_df if available
    if not unified_df.empty and 'original_query' in unified_df.columns:
        for _, row in unified_df.iterrows():
            query = str(row['original_query']).strip()
            answer = str(row['response']).strip()
            category = str(row['category']).strip()
            
            # Check if this response already exists
            duplicate = False
            for existing in final_rows:
                if answer.lower() in existing['answer'].lower() or existing['answer'].lower() in answer.lower():
                    duplicate = True
                    break
            
            if not duplicate and len(answer) > 50:  # Only add substantial responses
                final_rows.append({
                    'category': category,
                    'subcategory': query,
                    'context_keywords': ', '.join(query.lower().split()[:10]),
                    'answer': answer,
                    'notes': f"Source: unified_responses"
                })
    
    # Create final dataframe
    final_df = pd.DataFrame(final_rows)
    
    # Remove exact duplicates
    final_df = final_df.drop_duplicates(subset=['category', 'subcategory', 'answer'])
    
    # Save reconciled dataset
    final_df.to_parquet('final_unified_responses.parquet')
    
    print(f"\nFinal reconciled dataset:")
    print(f"Rows: {len(final_df)}")
    print(f"Columns: {list(final_df.columns)}")
    print(f"Data types:\n{final_df.dtypes}")
    
    # Show sample data
    print(f"\nSample rows:")
    for i in range(min(3, len(final_df))):
        row = final_df.iloc[i]
        print(f"\nRow {i+1}:")
        print(f"  Category: {row['category']}")
        print(f"  Subcategory: {row['subcategory']}")
        print(f"  Keywords: {row['context_keywords']}")
        print(f"  Answer: {row['answer'][:200]}...")
        print(f"  Notes: {row['notes']}")
    
    return final_df

if __name__ == "__main__":
    reconcile_datasets()