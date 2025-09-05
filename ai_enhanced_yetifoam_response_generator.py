#!/usr/bin/env python3
"""
YetiFoam Response Generator - AI Enhanced Edition
AI-powered interface using Anthropic Claude for intelligent query reasoning and relevant responses
"""

import streamlit as st
import pandas as pd
import os
from anthropic import Anthropic
from typing import List, Dict
import json

# Configure page
st.set_page_config(
    page_title="YetiFoam Response Generator - AI Enhanced",
    page_icon="🏠",
    layout="wide"
)

class AIEnhancedResponseGenerator:
    def __init__(self):
        """Initialize the AI-enhanced response generator"""
        self.dataset = None
        self.anthropic_client = None
        self.load_dataset()
        self.setup_anthropic()
    
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
    
    def setup_anthropic(self):
        """Setup Anthropic client with API key"""
        try:
            # Try to get API key from Streamlit secrets first
            api_key = None
            try:
                api_key = st.secrets.get("anthropic", {}).get("api_key")
            except:
                pass
            
            # Fallback to environment variable
            if not api_key:
                api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            if api_key and api_key != "your_api_key_here":
                self.anthropic_client = Anthropic(api_key=api_key)
                print("Anthropic client initialized successfully")
            else:
                self.anthropic_client = None
                print("No valid Anthropic API key found")
                
        except Exception as e:
            st.error(f"Error setting up Anthropic client: {e}")
            self.anthropic_client = None
    
    def create_dataset_context(self, query: str) -> str:
        """Create relevant dataset context for the query"""
        if self.dataset is None or len(self.dataset) == 0:
            return "No dataset available."
        
        # Find potentially relevant entries based on keywords
        query_lower = query.lower()
        relevant_entries = []
        
        for idx, row in self.dataset.iterrows():
            searchable_text = f"{row['category']} {row['subcategory']} {row['context_keywords']} {row['answer']}"
            
            # Basic keyword matching for context
            if any(word in searchable_text.lower() for word in query_lower.split() if len(word) > 2):
                relevant_entries.append({
                    'category': row['category'],
                    'subcategory': row['subcategory'],
                    'keywords': row['context_keywords'],
                    'answer_preview': row['answer'][:200] + "..." if len(row['answer']) > 200 else row['answer']
                })
        
        # Limit to top 5 most relevant entries
        context = "Relevant dataset entries:\n"
        for i, entry in enumerate(relevant_entries[:5]):
            context += f"{i+1}. Category: {entry['category']} - {entry['subcategory']}\n"
            context += f"   Keywords: {entry['keywords']}\n"
            context += f"   Content: {entry['answer_preview']}\n\n"
        
        return context
    
    def generate_ai_responses(self, query: str, num_responses: int = 2) -> List[Dict]:
        """Generate responses using Claude API with reasoning"""
        if not self.anthropic_client:
            return [{
                'reasoning': "API key required for advanced reasoning",
                'category': 'API Error',
                'subcategory': 'Missing API Key',
                'social_media_response': "API key required for advanced reasoning—set ANTHROPIC_API_KEY in environment variables or .streamlit/secrets.toml under [anthropic] api_key = 'your_key_here'"
            }]
        
        # Create dataset context
        dataset_context = self.create_dataset_context(query)
        
        # System prompt for Claude
        system_prompt = """You are a helpful assistant for YetiFoam insulation. Analyze the user's query, reason step-by-step about its intent, match it to relevant topics from the dataset (e.g., safety, toxicity, installation), and generate 2-3 concise, professional social media responses (100-300 words each) that directly address the query. 

Use dataset facts on polyurethane safety, formaldehyde-free status, compliance, etc., for queries like 'is it toxic'. End each with a call-to-action. Ensure relevance—do not divert to unrelated topics like fire safety for toxicity questions.

Format your response as JSON with this structure:
{
  "reasoning": "Your step-by-step analysis of the query intent and relevant dataset topics",
  "responses": [
    {
      "category": "Main topic category",
      "subcategory": "Specific topic", 
      "social_media_response": "Complete social media ready response with empathetic start, key facts, and CTA"
    }
  ]
}"""

        # User prompt with query and dataset context
        user_prompt = f"""Query: "{query}"

{dataset_context}

Please analyze this query and generate {num_responses} relevant social media responses based on the YetiFoam dataset provided."""

        try:
            # Make API call to Claude
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse the response
            response_text = message.content[0].text
            
            try:
                # Try to parse JSON response
                parsed_response = json.loads(response_text)
                
                responses = []
                reasoning = parsed_response.get('reasoning', 'No reasoning provided')
                
                for i, resp in enumerate(parsed_response.get('responses', [])[:num_responses]):
                    responses.append({
                        'reasoning': reasoning if i == 0 else '',  # Only show reasoning on first response
                        'category': resp.get('category', 'Generated Response'),
                        'subcategory': resp.get('subcategory', f'AI Response {i+1}'),
                        'social_media_response': resp.get('social_media_response', 'No response generated')
                    })
                
                return responses if responses else self.generate_fallback_response(query)
                
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract content manually
                return [{
                    'reasoning': 'AI generated response (JSON parsing failed)',
                    'category': 'AI Generated',
                    'subcategory': 'Claude Response',
                    'social_media_response': response_text[:500] + "... Contact us at yetifoam.com.au/contact for more info."
                }]
                
        except Exception as e:
            st.error(f"Error calling Claude API: {e}")
            return self.generate_fallback_response(query)
    
    def generate_fallback_response(self, query: str) -> List[Dict]:
        """Generate fallback response when API fails"""
        return [{
            'reasoning': 'Fallback response due to API error',
            'category': 'General',
            'subcategory': 'Contact Support',
            'social_media_response': f"Thanks for your question about '{query}'. For detailed information about YetiFoam products, please contact our expert team at yetifoam.com.au/contact who can provide specific guidance tailored to your needs."
        }]

def main():
    """Main Streamlit app"""
    # Initialize generator
    if 'ai_generator' not in st.session_state:
        st.session_state.ai_generator = AIEnhancedResponseGenerator()
    
    generator = st.session_state.ai_generator
    
    # Title and description
    st.title("🤖 YetiFoam Response Generator - AI Enhanced Edition")
    st.markdown("AI-powered responses using Claude for intelligent query reasoning")
    
    # API Key status indicator
    if generator.anthropic_client:
        st.success("✅ Claude API connected")
    else:
        st.warning("⚠️ Claude API key required - set ANTHROPIC_API_KEY environment variable")
        st.info("💡 Set your API key in environment variables or add to .streamlit/secrets.toml:\n```\n[anthropic]\napi_key = 'your_api_key_here'\n```")
    
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
    if st.button("🎯 Generate AI Responses", type="primary", use_container_width=True):
        if query.strip():
            with st.spinner("Claude is analyzing your query and generating responses..."):
                responses = generator.generate_ai_responses(query.strip(), num_responses)
                
                st.success(f"Generated {len(responses)} AI response(s)")
                
                # Display responses
                for i, response in enumerate(responses, 1):
                    with st.expander(f"🤖 AI Response {i}: {response['category']} - {response['subcategory']}", expanded=True):
                        
                        # Show reasoning for first response
                        if i == 1 and response.get('reasoning'):
                            st.markdown("**🧠 AI Reasoning:**")
                            st.info(response['reasoning'])
                            st.markdown("---")
                        
                        # Social media response
                        st.markdown("**📱 Social Media Ready Response:**")
                        response_text = response['social_media_response']
                        st.markdown(f"*{response_text}*")
                        
                        # Character count
                        char_count = len(response_text)
                        if char_count <= 280:
                            st.success(f"✅ {char_count} characters (Twitter/X friendly)")
                        elif char_count <= 500:
                            st.info(f"ℹ️ {char_count} characters (LinkedIn/Facebook friendly)")
                        else:
                            st.warning(f"⚠️ {char_count} characters (may need trimming for some platforms)")
                        
                        # Copy button
                        st.code(response_text, language=None)
                
        else:
            st.warning("Please enter a question or comment first.")
    
    # Footer
    st.markdown("---")
    st.markdown("*AI-enhanced interface using Anthropic Claude for intelligent query analysis and relevant response generation*")

if __name__ == "__main__":
    main()