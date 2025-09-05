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
        """Create relevant dataset context for the query with enhanced safety prioritization"""
        if self.dataset is None or len(self.dataset) == 0:
            return "No dataset available."
        
        query_lower = query.lower()
        relevant_entries = []
        
        # Enhanced safety/toxicity keywords for better detection
        safety_keywords = ['toxic', 'toxicity', 'safe', 'safety', 'formaldehyde', 'polyurethane', 
                          'chemical', 'health', 'harmful', 'dangerous', 'poisonous', 'hazard',
                          'material', 'composition', 'made', 'contains']
        
        # Check if this is a safety-related query
        is_safety_query = any(keyword in query_lower for keyword in safety_keywords)
        
        # For toxicity queries, prioritize specific safety entries first
        if 'toxic' in query_lower or 'toxicity' in query_lower:
            safety_priorities = [
                ('formaldehyde', 15),  # Highest priority for formaldehyde-free info
                ('polyurethane', 12),  # High priority for polyurethane safety
                ('chemical', 10),      # Chemical compatibility
                ('fibres', 8),         # Fiber release information
                ('particles', 8)       # Particle information
            ]
        else:
            safety_priorities = []
        
        for idx, row in self.dataset.iterrows():
            searchable_text = f"{row['category']} {row['subcategory']} {row['context_keywords']} {row['answer']}".lower()
            
            # Calculate relevance score
            score = 0
            query_words = [word for word in query_lower.split() if len(word) > 2]
            
            # Base relevance from word matching
            for word in query_words:
                if word in searchable_text:
                    score += 2  # Increased base score
            
            # Special toxicity query handling
            if 'toxic' in query_lower:
                # Massive boost for formaldehyde-free content
                if 'formaldehyde' in searchable_text and 'no formaldehyde' in searchable_text:
                    score += 20
                # High boost for polyurethane safety content
                elif 'polyurethane' in searchable_text:
                    score += 15
                # Boost for other safety content
                elif any(word in searchable_text for word in ['chemical', 'compatible', 'safe', 'fibres', 'particles']):
                    score += 8
            
            # General safety query bonuses
            if is_safety_query:
                # High priority for Fire Safety & Compliance category
                if row['category'] == 'Fire Safety & Compliance':
                    score += 12
                # Medium priority for safety keywords in any field
                elif any(keyword in searchable_text for keyword in safety_keywords):
                    score += 6
                # Apply special priority bonuses for toxicity queries
                for priority_word, bonus in safety_priorities:
                    if priority_word in searchable_text:
                        score += bonus
            
            # Only include entries with some relevance
            if score > 0:
                relevant_entries.append({
                    'score': score,
                    'category': row['category'],
                    'subcategory': row['subcategory'],
                    'keywords': row['context_keywords'],
                    'full_answer': row['answer'],
                    'answer_preview': row['answer'][:300] + "..." if len(row['answer']) > 300 else row['answer']
                })
        
        # Sort by relevance score (highest first)
        relevant_entries.sort(key=lambda x: x['score'], reverse=True)
        
        # Create context with safety prioritization
        if is_safety_query and len(relevant_entries) > 0:
            context = "CRITICAL SAFETY INFORMATION - YetiFoam Dataset:\n\n"
        else:
            context = "Relevant dataset entries:\n\n"
        
        # Include top entries with enhanced context for safety queries
        max_entries = 8 if is_safety_query else 6
        for i, entry in enumerate(relevant_entries[:max_entries]):
            context += f"{i+1}. [{entry['category']} - {entry['subcategory']}] (Score: {entry['score']})\n"
            context += f"   Keywords: {entry['keywords']}\n"
            
            # For high-scoring safety entries, include full content
            if is_safety_query and entry['score'] >= 8:
                context += f"   FULL CONTENT: {entry['full_answer']}\n\n"
            else:
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
        
        # Enhanced system prompt for Claude with improved safety focus
        system_prompt = """You are an expert YetiFoam insulation assistant specializing in safety and product information.

CRITICAL INSTRUCTIONS FOR TOXICITY/SAFETY QUERIES:
When users ask "is it toxic?", "is it safe?", or similar health/safety questions:

1. IMMEDIATELY HIGHLIGHT these key safety facts from the dataset:
   - YetiFoam contains NO FORMALDEHYDE (unlike some other insulation products)
   - Made from POLYURETHANE - the same safe material in fridges, mattresses, furniture, and HVAC systems
   - Does NOT release fibres or particles during or after installation  
   - Chemically compatible with electrical systems and PVC cables
   - Meets Australian fire safety standards

2. FOCUS ON MATERIAL SAFETY, not fire safety or installation topics
3. USE REASSURING, FACTUAL LANGUAGE that addresses toxicity concerns directly
4. COMPARE to everyday safe products people know (fridges, mattresses, furniture)

For toxicity questions, your responses must emphasize YetiFoam's safety through:
- Formaldehyde-free composition
- Safe polyurethane material (same as household items)
- No harmful particle or fibre release

Analyze the query intent and generate relevant social media responses that directly address safety concerns using the dataset facts provided.

Return ONLY valid JSON in this exact format:
{
  "reasoning": "Brief analysis of the safety query and key facts to highlight",
  "responses": [
    {
      "category": "Safety",
      "subcategory": "Material Safety",
      "social_media_response": "Direct safety answer + key facts + yetifoam.com.au/contact. Under 280 chars."
    }
  ]
}

Ensure all responses are factual, reassuring, and end with the contact URL."""

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
                # Clean response text for better JSON parsing
                clean_response = response_text.strip()
                
                # Try to extract JSON if it's embedded in markdown or other text
                json_start = clean_response.find('{')
                json_end = clean_response.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = clean_response[json_start:json_end]
                else:
                    json_text = clean_response
                
                # Try to parse JSON response
                parsed_response = json.loads(json_text)
                
                responses = []
                reasoning = parsed_response.get('reasoning', 'AI analysis completed')
                
                response_list = parsed_response.get('responses', [])
                if not response_list:
                    # Fallback if no responses array found
                    return self.generate_fallback_response(query)
                
                for i, resp in enumerate(response_list[:num_responses]):
                    social_response = resp.get('social_media_response', 'No response generated')
                    
                    # Ensure response ends with contact info if not present
                    if 'yetifoam.com.au/contact' not in social_response.lower():
                        if len(social_response) < 240:  # Leave room for contact info
                            social_response += " Contact us at yetifoam.com.au/contact for more info."
                    
                    responses.append({
                        'reasoning': reasoning if i == 0 else '',  # Only show reasoning on first response
                        'category': resp.get('category', 'Safety Response'),
                        'subcategory': resp.get('subcategory', f'AI Response {i+1}'),
                        'social_media_response': social_response
                    })
                
                return responses if responses else self.generate_fallback_response(query)
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Enhanced fallback with better error handling
                print(f"JSON parsing error: {e}")
                print(f"Raw response: {response_text[:200]}...")
                
                # Try to extract useful content even if JSON parsing fails
                if 'formaldehyde' in response_text.lower() or 'polyurethane' in response_text.lower():
                    # Likely contains safety info, try to use it
                    clean_text = response_text.replace('```json', '').replace('```', '').strip()
                    if len(clean_text) > 300:
                        clean_text = clean_text[:280] + "..."
                    
                    return [{
                        'reasoning': 'Response extracted from AI (JSON parsing failed but safety content detected)',
                        'category': 'Safety Information',
                        'subcategory': 'Material Safety',
                        'social_media_response': clean_text + " More info at yetifoam.com.au/contact"
                    }]
                else:
                    return self.generate_fallback_response(query)
                
        except Exception as e:
            st.error(f"Error calling Claude API: {e}")
            return self.generate_fallback_response(query)
    
    def generate_fallback_response(self, query: str) -> List[Dict]:
        """Generate fallback response when API fails"""
        query_lower = query.lower()
        
        # Enhanced fallback for safety/toxicity questions
        if any(word in query_lower for word in ['toxic', 'safe', 'safety', 'health', 'harmful']):
            return [{
                'reasoning': 'Fallback safety response - YetiFoam is formaldehyde-free polyurethane (same material used in fridges and furniture)',
                'category': 'Safety Information',
                'subcategory': 'Material Safety',
                'social_media_response': "YetiFoam is safe! It's formaldehyde-free polyurethane - the same material used in fridges, mattresses & furniture. No harmful fibres or particles. Contact yetifoam.com.au/contact for detailed safety info."
            }]
        
        # General fallback
        return [{
            'reasoning': 'Fallback response due to API error',
            'category': 'General Information',
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