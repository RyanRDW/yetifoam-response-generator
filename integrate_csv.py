#!/usr/bin/env python3
"""
Integrate unique responses from all_extracted_responses.csv into final dataset
"""
import pandas as pd

def integrate_csv_data():
    # Load datasets
    print("Loading datasets for integration...")
    csv_df = pd.read_csv('all_extracted_responses.csv')
    final_df = pd.read_parquet('final_unified_responses.parquet')
    
    print(f"CSV dataset: {csv_df.shape}")
    print(f"Current final dataset: {final_df.shape}")
    
    # Convert CSV data to final schema
    new_rows = []
    added_count = 0
    skipped_count = 0
    
    for _, csv_row in csv_df.iterrows():
        query = str(csv_row['query']).strip()
        response = str(csv_row['response']).strip()
        category = str(csv_row['category']).strip()
        
        # Skip if response is too short or empty
        if len(response) < 50:
            skipped_count += 1
            continue
        
        # Check for duplicates in final dataset
        is_duplicate = False
        for _, final_row in final_df.iterrows():
            final_answer = str(final_row['answer']).strip()
            
            # More precise duplicate detection
            if len(response) > 100 and len(final_answer) > 100:
                # Check for 80% overlap in either direction
                shorter = response if len(response) < len(final_answer) else final_answer
                longer = final_answer if len(response) < len(final_answer) else response
                
                if shorter.lower() in longer.lower() and len(shorter) > len(longer) * 0.8:
                    is_duplicate = True
                    break
        
        # Also check against new rows being added
        if not is_duplicate:
            for new_row in new_rows:
                if response.lower() in new_row['answer'].lower() or new_row['answer'].lower() in response.lower():
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            # Parse query for subcategory and keywords
            if '\n' in query:
                lines = query.split('\n')
                subcategory = lines[1].strip() if len(lines) > 1 else lines[0].strip()
            else:
                subcategory = query
            
            # Extract keywords from query
            keywords = []
            for line in query.split('\n'):
                keywords.extend(line.lower().split())
            keywords = [w for w in keywords if len(w) > 2]
            keywords = list(set(keywords[:15]))  # Limit and dedupe
            
            new_rows.append({
                'category': category,
                'subcategory': subcategory,
                'context_keywords': ', '.join(keywords),
                'answer': response,
                'notes': f"Source: {csv_row['source']}, ID: {csv_row['id']}"
            })
            added_count += 1
        else:
            skipped_count += 1
    
    print(f"\nIntegration results:")
    print(f"Added {added_count} unique responses from CSV")
    print(f"Skipped {skipped_count} duplicate/invalid responses")
    
    # Combine with existing final dataset
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        integrated_df = pd.concat([final_df, new_df], ignore_index=True)
        
        # Final deduplication pass
        integrated_df = integrated_df.drop_duplicates(subset=['category', 'subcategory', 'answer'])
        
        # Save updated final dataset
        integrated_df.to_parquet('final_unified_responses.parquet')
        
        print(f"Updated final dataset shape: {integrated_df.shape}")
        print(f"Net addition: {len(integrated_df) - len(final_df)} rows")
        
        return {
            'action': 'integrated',
            'justification': f'Added {added_count} unique responses from CSV',
            'original_csv_rows': len(csv_df),
            'added_rows': added_count,
            'skipped_rows': skipped_count,
            'final_dataset_rows': len(integrated_df)
        }
    else:
        return {
            'action': 'no_integration',
            'justification': 'No unique responses found in CSV after deduplication',
            'original_csv_rows': len(csv_df),
            'added_rows': 0,
            'skipped_rows': skipped_count,
            'final_dataset_rows': len(final_df)
        }

if __name__ == "__main__":
    result = integrate_csv_data()
    print(f"\nIntegration result: {result}")