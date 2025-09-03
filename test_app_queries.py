#!/usr/bin/env python3
"""
Test the repaired Yetifoam app with challenging queries
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from yetifoam_enhanced_final_streamlit_app import YetifoamEnhancedResponseGenerator

def test_app_with_queries():
    """Test the app with 10 challenging queries"""
    
    # Initialize the generator
    try:
        generator = YetifoamEnhancedResponseGenerator()
        print("✅ App initialized successfully")
        print(f"Dataset loaded: {len(generator.dataset)} responses")
    except Exception as e:
        print(f"❌ Failed to initialize app: {e}")
        return
    
    # Test queries (4 failing + 6 additional)
    test_queries = [
        # Original failing queries
        "what about cables in the subfloor?",
        "IS IT SAFE FOR DOGS INCASE THEY EAT IT?",
        "It would be a nightmare to rewire under there",  
        "how much pm2",
        
        # Additional challenging queries
        "R-value per inch",
        "installation cost",
        "can I paint over spray foam",
        "does it meet fire safety standards",
        "will it stop condensation problems",
        "sound dampening properties"
    ]
    
    print("\n=== TESTING APP WITH 10 CHALLENGING QUERIES ===")
    
    success_count = 0
    results_table = []
    
    for i, query in enumerate(test_queries, 1):
        try:
            # Search for responses
            results = generator.search_responses(query, max_results=1)
            
            if results and len(results) > 0:
                result = results[0]
                response = generator.get_response_text(result)
                confidence = result.get('confidence', 0)
                category = result.get('category', 'Unknown')
                
                # Check if result is usable (confidence > 50 and response exists)
                is_success = confidence >= 50 and len(response) > 20
                success_count += is_success
                
                status = "✅ SUCCESS" if is_success else "❌ POOR"
                
                print(f"\n{i}. Query: '{query}'")
                print(f"   Status: {status}")  
                print(f"   Confidence: {confidence:.1f}%")
                print(f"   Category: {category}")
                print(f"   Response: {response[:100]}...")
                
                results_table.append({
                    'Query': query,
                    'Success': '✅' if is_success else '❌',
                    'Confidence': f"{confidence:.1f}%",
                    'Response_Preview': response[:60] + "..." if len(response) > 60 else response
                })
            else:
                print(f"\n{i}. Query: '{query}'")
                print("   Status: ❌ NO RESULTS")
                results_table.append({
                    'Query': query,
                    'Success': '❌',
                    'Confidence': '0%',
                    'Response_Preview': 'No results found'
                })
                
        except Exception as e:
            print(f"\n{i}. Query: '{query}'")
            print(f"   Status: ❌ ERROR - {e}")
            results_table.append({
                'Query': query,
                'Success': '❌',
                'Confidence': '0%',
                'Response_Preview': f'Error: {e}'
            })
    
    # Calculate success rate
    success_rate = (success_count / len(test_queries)) * 100
    
    print(f"\n=== TEST RESULTS SUMMARY ===")
    print(f"Success Rate: {success_rate:.1f}% ({success_count}/{len(test_queries)})")
    print(f"Target: 100% usability")
    
    # Print results table
    print(f"\n=== DETAILED RESULTS TABLE ===")
    for result in results_table:
        print(f"Query: {result['Query']}")
        print(f"  → Success: {result['Success']} | Confidence: {result['Confidence']}")
        print(f"  → Response: {result['Response_Preview']}")
        print()
    
    # Final verdict
    if success_rate >= 90:
        print("🎉 EXCELLENT: App is ready for production use!")
        return True
    elif success_rate >= 70:
        print("⚠️ GOOD: App works well but has minor issues")
        return True
    else:
        print("❌ NEEDS WORK: App requires more improvements")
        return False

if __name__ == "__main__":
    success = test_app_with_queries()
    exit(0 if success else 1)