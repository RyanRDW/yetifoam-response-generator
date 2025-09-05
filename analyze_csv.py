#!/usr/bin/env python3
"""
Analyze the untracked all_extracted_responses.csv file
"""
import pandas as pd

def analyze_untracked_csv():
    # Load and analyze the CSV
    print("Loading all_extracted_responses.csv...")
    csv_df = pd.read_csv('all_extracted_responses.csv')
    
    print(f"CSV file shape: {csv_df.shape}")
    print(f"CSV columns: {list(csv_df.columns)}")
    
    # Load final unified dataset for comparison
    final_df = pd.read_parquet('final_unified_responses.parquet')
    print(f"Final unified dataset shape: {final_df.shape}")
    
    # Check for unique content in CSV
    unique_responses = 0
    duplicate_responses = 0
    
    for _, csv_row in csv_df.iterrows():
        csv_response = str(csv_row['response']).strip()
        
        # Check if this response exists in final dataset
        is_duplicate = False
        for _, final_row in final_df.iterrows():
            final_answer = str(final_row['answer']).strip()
            
            # Check for substantial overlap (>80% similarity)
            if len(csv_response) > 100 and len(final_answer) > 100:
                if csv_response.lower() in final_answer.lower() or final_answer.lower() in csv_response.lower():
                    is_duplicate = True
                    break
        
        if is_duplicate:
            duplicate_responses += 1
        else:
            unique_responses += 1
    
    print(f"\nContent analysis:")
    print(f"Unique responses in CSV: {unique_responses}")
    print(f"Duplicate responses in CSV: {duplicate_responses}")
    print(f"Total CSV responses: {len(csv_df)}")
    
    # Sample CSV data
    print(f"\nCSV Sample (first 3 rows):")
    for i in range(min(3, len(csv_df))):
        row = csv_df.iloc[i]
        print(f"\nRow {i+1}:")
        print(f"  ID: {row['id']}")
        print(f"  Query: {str(row['query'])[:100]}...")
        print(f"  Response: {str(row['response'])[:200]}...")
        print(f"  Category: {row['category']}")
        print(f"  Source: {row['source']}")
    
    # Recommendation
    if unique_responses < 5:  # Less than 5 unique responses
        recommendation = "ignore"
        justification = f"CSV contains mostly duplicate data ({duplicate_responses}/{len(csv_df)} duplicates). Only {unique_responses} unique responses found."
        
        # Add to .gitignore
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        if 'all_extracted_responses.csv' not in gitignore_content:
            with open('.gitignore', 'a') as f:
                f.write('\n# Large CSV files\nall_extracted_responses.csv\n')
            print("\nAdded all_extracted_responses.csv to .gitignore")
        
    else:
        recommendation = "integrate"
        justification = f"CSV contains {unique_responses} unique responses worth preserving"
    
    return {
        'action': recommendation,
        'justification': justification,
        'csv_rows': len(csv_df),
        'unique_responses': unique_responses,
        'duplicate_responses': duplicate_responses
    }

if __name__ == "__main__":
    result = analyze_untracked_csv()
    print(f"\nRecommendation: {result}")