#!/usr/bin/env python3
"""
YetiFoam Response Generator - Simple Edition
Simplified interface for marketing staff to generate social media responses
"""

import streamlit as st
import pandas as pd
import os
from fuzzywuzzy import fuzz, process
from typing import List, Dict
import re

# Configure page
st.set_page_config(
    page_title="YetiFoam Response Generator - Simple",
    page_icon="🏠",
    layout="wide"
)

class SimpleResponseGenerator:
    def __init__(self):
        """Initialize the simple response generator"""
        self.dataset = None
        self.load_dataset()
    
    def load_dataset(self):
        """Load the updated responses dataset"""
        try:
            # Try to load the updated parquet file first
            dataset_path = "updated_final_unified_responses.parquet"
            if os.path.exists(dataset_path):
                self.dataset = pd.read_parquet(dataset_path)
            else:
                # Fallback to CSV if parquet doesn't exist
                dataset_path = "updated_final_yetifoam_responses.csv"
                self.dataset = pd.read_csv(dataset_path)
            
            print(f"Loaded dataset with {len(self.dataset)} responses from {dataset_path}")
            
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            self.dataset = pd.DataFrame()
    
    def clean_response_for_social_media(self, response: str, query: str) -> str:
        """Clean and format response for social media"""
        # Remove HTML comments and excessive formatting
        response = re.sub(r'<!--.*?-->', '', response)
        response = re.sub(r'\s+', ' ', response).strip()
        
        # Add empathetic opening based on query type
        empathy_starters = {
            'toxic': "We understand your concern about safety.",
            'safe': "Great question about safety!",
            'install': "Thanks for asking about installation.",
            'cost': "We appreciate your interest in value.",
            'moisture': "Excellent question about moisture control.",
            'fire': "Important question about fire safety."
        }
        
        query_lower = query.lower()
        empathy = "Thanks for your question."
        for key, starter in empathy_starters.items():
            if key in query_lower:
                empathy = starter
                break
        
        # Ensure response isn't too long for social media
        if len(response) > 280:
            # Find a good breaking point
            sentences = response.split('. ')
            truncated = []
            char_count = 0
            
            for sentence in sentences:
                if char_count + len(sentence) + 2 <= 250:  # Leave room for ending
                    truncated.append(sentence)
                    char_count += len(sentence) + 2
                else:
                    break
            
            response = '. '.join(truncated)
            if not response.endswith('.'):
                response += '.'
        
        # Add call to action
        cta = " Contact us at yetifoam.com.au/contact for more info."
        
        # Combine with proper spacing
        final_response = f"{empathy} {response}{cta}"
        
        return final_response
    
    def find_best_matches(self, query: str, num_responses: int = 2) -> List[Dict]:
        """Find best matching responses using fuzzy matching"""
        if self.dataset is None or len(self.dataset) == 0:
            return []
        
        matches = []
        
        # Create searchable text combining multiple fields
        for idx, row in self.dataset.iterrows():
            searchable_text = f"{row['category']} {row['subcategory']} {row['context_keywords']} {row['answer']}"
            
            # Calculate fuzzy match scores
            token_sort_score = fuzz.token_sort_ratio(query.lower(), searchable_text.lower())
            token_set_score = fuzz.token_set_ratio(query.lower(), searchable_text.lower())
            partial_score = fuzz.partial_ratio(query.lower(), searchable_text.lower())
            
            # Weighted average score
            combined_score = (token_sort_score * 0.4 + token_set_score * 0.4 + partial_score * 0.2)
            
            if combined_score >= 40:  # Minimum threshold
                matches.append({
                    'score': combined_score,
                    'category': row['category'],
                    'subcategory': row['subcategory'],
                    'answer': row['answer'],
                    'original_answer': row['answer']
                })
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:num_responses]
    
    def generate_responses(self, query: str, num_responses: int = 2) -> List[Dict]:
        """Generate social media friendly responses"""
        best_matches = self.find_best_matches(query, num_responses)
        
        if not best_matches:
            return [{
                'category': 'No Match',
                'subcategory': 'Fallback',
                'answer': "No direct match found. Please refine your query or contact support at yetifoam.com.au/contact for specific assistance.",
                'social_media_response': "No direct match found. Please refine your query or contact support at yetifoam.com.au/contact for specific assistance."
            }]
        
        # Process each match for social media
        processed_responses = []
        for match in best_matches:
            social_response = self.clean_response_for_social_media(match['answer'], query)
            processed_responses.append({
                'category': match['category'],
                'subcategory': match['subcategory'],
                'answer': match['original_answer'],
                'social_media_response': social_response
            })
        
        return processed_responses

def main():
    """Main Streamlit app"""
    # Initialize generator
    if 'generator' not in st.session_state:
        st.session_state.generator = SimpleResponseGenerator()
    
    generator = st.session_state.generator
    
    # Title and description
    st.title("🏠 YetiFoam Response Generator - Simple Edition")
    st.markdown("Generate quick, accurate responses for social media comments and posts")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter a customer question or comment here:",
            placeholder="e.g., 'Is YetiFoam toxic?', 'How much clearance needed?', 'Fire safety?'"
        )
    
    with col2:
        num_responses = st.selectbox(
            "Number of responses:",
            options=[2, 3],
            index=0
        )
    
    # Generate button
    if st.button("🎯 Generate Responses", type="primary", use_container_width=True):
        if query.strip():
            with st.spinner("Generating responses..."):
                responses = generator.generate_responses(query.strip(), num_responses)
                
                st.success(f"Generated {len(responses)} response(s)")
                
                # Display responses
                for i, response in enumerate(responses, 1):
                    with st.expander(f"📝 Response {i}: {response['category']} - {response['subcategory']}", expanded=True):
                        
                        # Social media response
                        st.markdown("**Social Media Ready Response:**")
                        response_text = response['social_media_response']
                        st.markdown(f"*{response_text}*")
                        
                        # Character count
                        char_count = len(response_text)
                        if char_count <= 280:
                            st.success(f"✅ {char_count} characters (Twitter/X friendly)")
                        else:
                            st.warning(f"⚠️ {char_count} characters (may be too long for some platforms)")
                        
                        # Copy button
                        st.code(response_text, language=None)
                        
                        # Original answer in expander for reference
                        with st.expander("📖 See full original answer"):
                            st.markdown(response['answer'])
                
        else:
            st.warning("Please enter a question or comment first.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Simple interface for marketing staff to generate professional social media responses*")

if __name__ == "__main__":
    main()