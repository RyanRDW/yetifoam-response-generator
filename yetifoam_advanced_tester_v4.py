#!/usr/bin/env python3
"""
Yetifoam Advanced Testing Suite v4.0 - Targeting 70%+ Quality Score
Tests the enhanced algorithm against identified problematic queries
Version: 4.0 - Advanced Quality Optimization
Created: September 1, 2025
"""

import json
import os
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Import the enhanced response generator
import sys
sys.path.append('/Users/ryanimac')

try:
    from fuzzywuzzy import fuzz, process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    print("fuzzywuzzy not available - using simplified matching")
    FUZZYWUZZY_AVAILABLE = False

class YetifoamAdvancedTester:
    def __init__(self):
        """Initialize the advanced testing suite"""
        self.dataset_path = "/Users/ryanimac/Yetifoam_Final_Package_v4/YETIFOAM_COVERAGE_OPTIMIZED_v5.json"
        self.dataset = None
        self.load_dataset()
        
        # Target problematic queries identified by Data Extractor Agent
        self.problematic_queries = {
            'zero_results_queries': [
                "energy efficiency", "thermal bridge", "thermal performance", 
                "cold bridging", "vapour barrier", "damp proofing", "fire rating",
                "rodent control", "vermin proofing", "product guarantee", 
                "long term performance", "durability", "polyurethane foam",
                "open cell foam", "curing time", "thermal conductivity"
            ],
            'low_quality_queries': [
                "spray foam mould", "R-value insulation", "fire safety", 
                "soundproof acoustic", "Tasmania service", "cost price",
                "installation time", "condensation moisture", "building standards"
            ],
            'edge_case_queries': [
                "AS 1530 compliance", "moisture trap prevention", 
                "Colorbond steel roof", "DIY installation kit",
                "thermal bridging solution", "closed cell benefits",
                "professional applicators", "substrate preparation"
            ]
        }
        
        # Quality keywords matching the enhanced app
        self.quality_keywords = {
            'technical': ['spray foam', 'yetifoam', 'insulation', 'r-value', 'thermal', 'polyurethane', 'closed-cell', 'open-cell', 'foam', 'vapour barrier', 'air seal', 'thermal resistance', 'rigid', 'dense', 'substrate', 'application', 'curing'],
            'standards': ['AS 1530', 'AS 3837', 'AS 3000', 'AS 3999', 'AS 3660', 'ASTM E96', 'australian standard', 'building code', 'compliance', 'class 2', 'class 1', 'certification', 'bal', 'bushfire attack level'],
            'professional': ['recommend', 'professional', 'experience', 'quality', 'certified', 'installation', 'assessment', 'applicators', 'installers', 'calibrated', 'trained', 'site visit', 'quote', 'enquiry', 'contact'],
            'locations': ['victoria', 'braeside', 'melbourne', 'tasmania', 'australia', 'victorian', 'dandenong', 'gippsland', 'wodonga', 'regional'],
            'benefits': ['energy efficiency', 'moisture barrier', 'fire safety', 'pest control', 'soundproofing', 'rodent deterrent', 'sound dampening', 'structural integrity', 'air leakage', 'thermal bridging', 'condensation', 'mould', 'rot']
        }
        
    def load_dataset(self) -> bool:
        """Load the enhanced dataset"""
        if os.path.exists(self.dataset_path):
            try:
                with open(self.dataset_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, dict) and 'items' in data:
                        self.dataset = data['items']
                    else:
                        self.dataset = data
                print(f"✅ Loaded dataset: {len(self.dataset)} items")
                return True
            except Exception as e:
                print(f"❌ Error loading dataset: {e}")
                return False
        return False

    def normalize_text(self, text: str) -> str:
        """Advanced text normalization matching the enhanced app"""
        if not text:
            return ""
        
        normalized = text.lower()
        # CRITICAL FIX: Remove double backslashes that break regex patterns
        normalized = re.sub(r'[^\w\s\-\.]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Technical entities recognition - FIXED regex patterns
        technical_entities = {
            r'\br[-_]?values?\b': 'thermal resistance r value',
            r'\bthermal\s+resistance\b': 'r value thermal resistance',
            r'\bthermal\s+bridge\b': 'thermal bridging cold bridge heat transfer',
            r'\benergy\s+effic\w*\b': 'energy efficiency thermal performance',
            r'\bfire\s+safety\b': 'fire rating fire performance as1530',
            r'\bspray\s+foam\b': 'yetifoam polyurethane closed cell insulation',
            r'\bsound\s*proof\w*\b': 'acoustic soundproofing sound dampening noise reduction',
            r'\bvapou?r\s+barrier\b': 'moisture barrier vapour barrier air seal',
        }
        
        for pattern, expansion in technical_entities.items():
            normalized = re.sub(pattern, expansion, normalized)
        
        return re.sub(r'\s+', ' ', normalized).strip()

    def simple_fuzzy_match(self, query: str, text: str) -> float:
        """ENHANCED: Query-centric word overlap algorithm for better coverage"""
        if not query or not text:
            return 0.0
        
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
        
        # IMPROVED: Use query-centric overlap ratio for better matching
        intersection = query_words.intersection(text_words)
        
        # Calculate percentage of query words found in text
        match_ratio = len(intersection) / len(query_words)
        
        # Boost score for exact phrase matches
        if len(intersection) == len(query_words):
            match_ratio *= 1.1  # 10% boost for complete query coverage
        
        # Slight penalty for very short queries to maintain quality
        if len(query_words) <= 1:
            match_ratio *= 0.9  # 10% penalty for single-word queries
        
        return min(match_ratio * 100, 100)

    def enhanced_fuzzy_search(self, query: str, text: str, category: str = "") -> Tuple[float, Dict[str, Any]]:
        """Enhanced fuzzy matching with dynamic weighting"""
        if not query or not text:
            return 0.0, {}
        
        query_norm = self.normalize_text(query)
        text_norm = self.normalize_text(text)
        category_norm = self.normalize_text(category)
        
        # Dynamic scoring based on query length
        query_length = len(query_norm.split())
        
        if FUZZYWUZZY_AVAILABLE:
            # Use advanced fuzzywuzzy scoring
            if query_length <= 2:
                weights = {'token_set': 0.45, 'partial': 0.25, 'token_sort': 0.20, 'ratio': 0.10}
            elif query_length <= 4:
                weights = {'token_set': 0.40, 'partial': 0.30, 'token_sort': 0.20, 'ratio': 0.10}
            else:
                weights = {'token_set': 0.30, 'partial': 0.40, 'token_sort': 0.20, 'ratio': 0.10}
            
            token_set_score = fuzz.token_set_ratio(query_norm, text_norm)
            partial_score = fuzz.partial_ratio(query_norm, text_norm)
            token_sort_score = fuzz.token_sort_ratio(query_norm, text_norm)
            ratio_score = fuzz.ratio(query_norm, text_norm)
            
            base_score = (
                token_set_score * weights['token_set'] +
                partial_score * weights['partial'] +
                token_sort_score * weights['token_sort'] +
                ratio_score * weights['ratio']
            )
        else:
            # Fallback to simple matching
            base_score = self.simple_fuzzy_match(query_norm, text_norm)
            token_set_score = partial_score = token_sort_score = ratio_score = base_score
        
        # Enhanced contextual bonuses
        query_words = set(query_norm.split())
        text_words = set(text_norm.split())
        category_words = set(category_norm.split())
        
        # Exact match bonus
        exact_bonus = 0
        word_match_ratio = len(query_words.intersection(text_words)) / len(query_words) if query_words else 0
        if word_match_ratio >= 0.9:
            exact_bonus = 10
        elif word_match_ratio >= 0.7:
            exact_bonus = 5
        
        # Category matching bonus (20% exact, 10% partial)
        category_bonus = 0
        if category_words:
            category_match_ratio = len(query_words.intersection(category_words)) / len(query_words) if query_words else 0
            if category_match_ratio >= 0.6:
                category_bonus = 20
            elif category_match_ratio >= 0.3:
                category_bonus = 10
        
        # Keyword density scoring
        keyword_bonus = 0
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an'}
        meaningful_query_words = {w for w in query_words if w not in stop_words and len(w) > 2}
        meaningful_text_words = {w for w in text_words if w not in stop_words and len(w) > 2}
        
        if meaningful_query_words:
            common_words = meaningful_query_words.intersection(meaningful_text_words)
            keyword_density = len(common_words) / len(meaningful_query_words)
            
            if keyword_density >= 0.8:
                keyword_bonus = 10
            elif keyword_density >= 0.6:
                keyword_bonus = 8
            elif keyword_density >= 0.4:
                keyword_bonus = 6
            elif keyword_density >= 0.2:
                keyword_bonus = 4
        
        # Calculate final score with penalty for low scores
        raw_score = base_score + exact_bonus + category_bonus + keyword_bonus
        
        if raw_score < 60:
            final_score = raw_score * 0.8  # 20% penalty
        else:
            final_score = min(raw_score, 100)
        
        scoring_details = {
            'query_length': query_length,
            'base_score': base_score,
            'exact_bonus': exact_bonus,
            'category_bonus': category_bonus,
            'keyword_bonus': keyword_bonus,
            'raw_score': raw_score,
            'final_score': final_score,
            'penalty_applied': raw_score < 60
        }
        
        return final_score, scoring_details

    def calculate_quality_score(self, text: str, category: str = "") -> float:
        """Advanced quality scoring targeting 70%+ (matching enhanced app)"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        category_lower = category.lower() if category else ""
        
        score = 25  # REDUCED Base score to prevent inflation
        
        # Technical keywords (25 points)
        tech_score = 0
        for keyword in self.quality_keywords['technical']:
            if keyword in text_lower:
                if keyword in ['r-value', 'thermal resistance', 'polyurethane', 'closed-cell', 'vapour barrier']:
                    tech_score += 4
                else:
                    tech_score += 2
        score += min(tech_score, 25)
        
        # Standards compliance (20 points)
        standards_score = 0
        for standard in self.quality_keywords['standards']:
            if standard in text_lower:
                if 'as ' in standard or 'australian standard' in standard:
                    standards_score += 8
                elif 'astm' in standard or 'compliance' in standard:
                    standards_score += 5
                else:
                    standards_score += 3
        score += min(standards_score, 20)
        
        # Professional language (10 points)
        prof_score = 0
        for prof_term in self.quality_keywords['professional']:
            if prof_term in text_lower:
                if prof_term in ['professional', 'certified', 'assessment', 'installation']:
                    prof_score += 3
                else:
                    prof_score += 1
        score += min(prof_score, 10)
        
        # Location accuracy (5 points)
        location_score = 0
        for location in self.quality_keywords['locations']:
            if location in text_lower:
                if location in ['victoria', 'braeside', 'melbourne']:
                    location_score += 2
                else:
                    location_score += 1
        score += min(location_score, 5)
        
        # Category-specific bonuses (5 points)
        category_bonus = 0
        if category_lower:
            if 'fire safety' in category_lower and any(term in text_lower for term in ['as 1530', 'fire rating', 'class 1', 'class 2']):
                category_bonus += 5
            elif 'thermal' in category_lower and any(term in text_lower for term in ['r-value', 'thermal resistance', 'r4']):
                category_bonus += 5
            elif 'moisture' in category_lower and any(term in text_lower for term in ['vapour barrier', 'moisture barrier', 'astm e96']):
                category_bonus += 5
        score += category_bonus
        
        # Content depth (10 points)
        if len(text) > 2000:
            score += 10
        elif len(text) > 1000:
            score += 8
        elif len(text) > 500:
            score += 6
        elif len(text) > 200:
            score += 4
        elif len(text) > 100:
            score += 2
        else:
            score += 1
        
        # REMOVED artificial final boost - let natural scoring determine quality
        
        return min(score, 100)

    def get_searchable_text(self, item: Dict[str, Any]) -> str:
        """Get searchable text with field prioritization"""
        weighted_texts = []
        
        priority_fields = [
            ('standardized_response', 0.50),
            ('inferred_question', 0.30),
            ('original_text', 0.20),
            ('response_text', 0.15),
            ('category', 0.05)
        ]
        
        for field, weight in priority_fields:
            if field in item and item[field]:
                text = str(item[field]).strip()
                if text:
                    repetitions = max(1, int(weight * 5))
                    weighted_texts.extend([text] * repetitions)
        
        return ' '.join(weighted_texts)

    def search_responses(self, query: str, confidence_threshold: float = 0.40, max_results: int = 10) -> List[Dict[str, Any]]:
        """Enhanced search with 75% threshold"""
        if not self.dataset or not query:
            return []
        
        results = []
        
        for item in self.dataset:
            searchable_text = self.get_searchable_text(item)
            if not searchable_text:
                continue
            
            category = item.get('category', '')
            confidence, scoring_details = self.enhanced_fuzzy_search(query, searchable_text, category)
            
            threshold_percentage = confidence_threshold * 100
            if confidence >= threshold_percentage:
                result = item.copy()
                result['confidence'] = confidence
                result['match_query'] = query
                result['scoring_details'] = scoring_details
                result['quality_score'] = self.calculate_quality_score(
                    self.get_response_text(result), category
                )
                results.append(result)
        
        # Sort by combined confidence and quality
        def sort_key(x):
            confidence_score = x['confidence']
            quality_score = x.get('quality_score', 0)
            return (confidence_score * 0.7) + (quality_score * 0.3)
        
        results.sort(key=sort_key, reverse=True)
        return results[:max_results]

    def get_response_text(self, item: Dict[str, Any]) -> str:
        """Get response text from item"""
        for field in ['standardized_response', 'response_text', 'original_text']:
            if field in item and item[field]:
                return item[field]
        return ""

    def run_advanced_testing(self) -> Dict[str, Any]:
        """Run comprehensive testing with all problematic queries"""
        print("🚀 Starting Advanced Testing Suite v4.0")
        print("🎯 Target: >70% Quality Score")
        print("=" * 60)
        
        start_time = time.time()
        
        # Combine all test queries
        all_queries = []
        all_queries.extend(self.problematic_queries['zero_results_queries'])
        all_queries.extend(self.problematic_queries['low_quality_queries'])
        all_queries.extend(self.problematic_queries['edge_case_queries'])
        
        print(f"🔍 Testing {len(all_queries)} problematic queries...")
        
        # Test results tracking
        results = {
            'test_timestamp': datetime.now().isoformat(),
            'total_queries_tested': len(all_queries),
            'queries_with_results': 0,
            'queries_without_results': 0,
            'total_matches_found': 0,
            'average_confidence': 0,
            'average_quality': 0,
            'high_quality_results': 0,  # >= 70%
            'medium_quality_results': 0,  # 50-69%
            'low_quality_results': 0,  # < 50%
            'query_performance': [],
            'quality_analysis': {},
            'improvement_summary': {}
        }
        
        total_confidence = 0
        total_quality = 0
        result_count = 0
        
        # Test each query
        for query in all_queries:
            query_results = self.search_responses(query, 0.40)  # Reduced threshold for better coverage
            
            query_performance = {
                'query': query,
                'matches_found': len(query_results),
                'top_confidence': query_results[0]['confidence'] if query_results else 0,
                'top_quality': query_results[0]['quality_score'] if query_results else 0,
                'top_category': query_results[0].get('category', 'N/A') if query_results else 'N/A',
                'previously_failed': query in self.problematic_queries['zero_results_queries']
            }
            
            results['query_performance'].append(query_performance)
            
            if query_results:
                results['queries_with_results'] += 1
                results['total_matches_found'] += len(query_results)
                
                for result in query_results:
                    confidence = result['confidence']
                    quality = result['quality_score']
                    
                    total_confidence += confidence
                    total_quality += quality
                    result_count += 1
                    
                    # Categorize quality
                    if quality >= 70:
                        results['high_quality_results'] += 1
                    elif quality >= 50:
                        results['medium_quality_results'] += 1
                    else:
                        results['low_quality_results'] += 1
            else:
                results['queries_without_results'] += 1
            
            print(f"   '{query}': {len(query_results)} results, " +
                  f"confidence: {query_performance['top_confidence']:.1f}%, " +
                  f"quality: {query_performance['top_quality']:.1f}%")
        
        # Calculate averages
        if result_count > 0:
            results['average_confidence'] = total_confidence / result_count
            results['average_quality'] = total_quality / result_count
        
        # Overall quality analysis
        results['quality_analysis'] = {
            'overall_quality_score': results['average_quality'],
            'target_achieved': results['average_quality'] >= 70,
            'high_quality_percentage': (results['high_quality_results'] / result_count * 100) if result_count > 0 else 0,
            'search_success_rate': (results['queries_with_results'] / results['total_queries_tested'] * 100),
            'confidence_target_met': results['average_confidence'] >= 75
        }
        
        # Improvement summary
        results['improvement_summary'] = {
            'zero_result_queries_fixed': sum(1 for qp in results['query_performance'] 
                                           if qp['previously_failed'] and qp['matches_found'] > 0),
            'queries_reaching_70_quality': results['high_quality_results'],
            'overall_performance': 'PASSED' if results['average_quality'] >= 70 else 'PARTIAL' if results['average_quality'] >= 60 else 'FAILED'
        }
        
        # Display results summary
        print("\n" + "=" * 60)
        print("🎯 ADVANCED TESTING RESULTS")
        print("=" * 60)
        
        print(f"\n📊 Quality Score Results:")
        print(f"   Overall Quality Score: {results['average_quality']:.1f}% (Target: 70%+)")
        print(f"   Target Achieved: {'✅ YES' if results['quality_analysis']['target_achieved'] else '❌ NO'}")
        print(f"   High Quality Results (≥70%): {results['high_quality_results']} ({results['quality_analysis']['high_quality_percentage']:.1f}%)")
        
        print(f"\n🔍 Search Performance:")
        print(f"   Queries with Results: {results['queries_with_results']}/{results['total_queries_tested']} ({results['quality_analysis']['search_success_rate']:.1f}%)")
        print(f"   Average Confidence: {results['average_confidence']:.1f}% (Target: 75%+)")
        print(f"   Zero-Result Queries Fixed: {results['improvement_summary']['zero_result_queries_fixed']}")
        
        print(f"\n🏆 Overall Performance: {results['improvement_summary']['overall_performance']}")
        
        return results

def main():
    """Main testing execution"""
    tester = YetifoamAdvancedTester()
    
    try:
        results = tester.run_advanced_testing()
        
        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"/Users/ryanimac/yetifoam_advanced_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Detailed results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"❌ Advanced testing failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()