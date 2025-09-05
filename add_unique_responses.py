#!/usr/bin/env python3
"""
Add genuinely unique responses extracted from the enhanced data
"""
import pandas as pd

def add_unique_responses():
    # Load existing dataset
    existing_df = pd.read_parquet('final_unified_responses.parquet')
    print(f"Existing dataset: {existing_df.shape}")
    
    # Create unique entries with distinct subcategories
    unique_entries = [
        {
            'category': 'Installation & Application',
            'subcategory': 'Future low clearance product development',
            'context_keywords': 'development, winter, next, future, low clearance, minimal space, product',
            'answer': 'For homes with minimal underfloor clearance, a new solution is being developed and is expected to be available before next winter. Stay tuned to our social media channels for updates.',
            'notes': 'Enhanced extraction: Future product development for low clearance applications'
        },
        {
            'category': 'Fire Safety & Compliance',
            'subcategory': 'Detailed electrical compliance AS3000 AS3999',
            'context_keywords': 'AS3000, AS3999, electrical compliance, PVC compatibility, cable encasement, de-rating',
            'answer': 'YetiFoam is completely safe around electrics and is installed in full compliance with AS 3000 and AS 3999. It does not encase cables; a standard 30 mm application leaves a slight overspray, so there is no need to remove, rewire or reinstall cables. Cables fixed to studs are considered "partially surrounded," so de-rating is not required unless cables are fully surrounded by insulation for 400 mm or more, which is rare.',
            'notes': 'Enhanced extraction: Detailed electrical standards compliance'
        },
        {
            'category': 'Fire Safety & Compliance',
            'subcategory': 'Insurance policy compliance verification',
            'context_keywords': 'insurance, policy, AS4859.1, Australian-made, Victorian, compliance team',
            'answer': 'YetiFoam is made by Victorians for Victorians and complies with all relevant Australian Standards, including AS/NZS 4859.1 (the bulk insulation product standard) and AS 3999 (safe and compliant installation). Unless your insurance policy explicitly excludes Australian made, compliant products, there should be no issues. Our compliance team can review your policy if needed.',
            'notes': 'Enhanced extraction: Insurance compliance with team support offer'
        },
        {
            'category': 'Installation & Application',
            'subcategory': 'Specific clearance measurements 400-500mm',
            'context_keywords': '400mm, 500mm, clearance requirements, site conditions, measurement',
            'answer': 'Underfloor installation generally requires around 400 mm of clearance, though some projects may need 400-500 mm depending on site conditions. If your home has very little clearance, please contact us - every site is different, and we can discuss options.',
            'notes': 'Enhanced extraction: Precise clearance specifications with measurements'
        },
        {
            'category': 'Moisture Resistance', 
            'subcategory': 'Ventilation compatibility with subfloor vents',
            'context_keywords': 'subfloor ventilation, vents open, breathe, external air blocking, moisture meter testing',
            'answer': 'Installing YetiFoam does not block subfloor ventilation - vents remain open, and the insulation is applied above them so the subfloor can still breathe while cold external air is blocked from entering. Applicators test substrate using calibrated moisture meters; if levels exceed 19% installation is postponed until dry.',
            'notes': 'Enhanced extraction: Ventilation system compatibility details'
        },
        {
            'category': 'Moisture Resistance',
            'subcategory': 'ASTM E96 vapor permeability testing',
            'context_keywords': 'ASTM E96, vapor permeability, 1.0 perms, steel sheds, container homes, technical specification',
            'answer': 'Yetifoam acts as a vapour barrier with vapor permeability below 1.0 perms per ASTM E96, effectively preventing water ingress and condensation on steel or timber surfaces. It is particularly suitable for steel sheds and container homes, blocking interior condensation and rust by stopping moisture entry.',
            'notes': 'Enhanced extraction: Technical vapor barrier specifications with ASTM testing'
        },
        {
            'category': 'Moisture Resistance',
            'subcategory': 'Structural reinforcement and squeak reduction',
            'context_keywords': 'structural integrity, squeak reduction, joists bonding, floor reinforcement, sound dampening',
            'answer': 'Yetifoam bonds subfloors to joists, enhancing structural integrity and reducing squeaks; users often note stronger, quieter floors post-installation. The rigid layer dampens sound transmission through floors and maintains performance for the building\'s life without sagging or settling.',
            'notes': 'Enhanced extraction: Structural benefits beyond insulation'
        },
        {
            'category': 'Moisture Resistance',
            'subcategory': 'Pest deterrent properties with boron compounds',
            'context_keywords': 'boron compounds, pest deterrent, insects, rodents, infestation prevention, natural deterrent',
            'answer': 'The foam contains boron compounds as a natural deterrent to insects and rodents. The dense barrier provides no nesting material, is hard to gnaw through, and seals entry points to prevent infestations, offering comprehensive pest protection.',
            'notes': 'Enhanced extraction: Pest control benefits with boron compound details'
        },
        {
            'category': 'Energy Efficiency',
            'subcategory': 'Thermal bridging elimination',
            'context_keywords': 'thermal bridging, heat loss elimination, continuous barrier, drafts, energy efficiency',
            'answer': 'Yetifoam eliminates thermal bridging by creating a continuous barrier that fills gaps and crevices completely. This prevents heat loss that occurs with traditional insulation systems, significantly improving energy efficiency by stopping drafts and maintaining consistent temperatures.',
            'notes': 'Enhanced extraction: Energy efficiency through thermal bridging prevention'
        },
        {
            'category': 'Health & Safety',
            'subcategory': 'Polyurethane safety in everyday products',
            'context_keywords': 'polyurethane safety, everyday products, fridges, mattresses, HVAC, carpet underlay, furniture',
            'answer': 'Polyurethane is widely used in everyday products such as fridges, mattresses, HVAC units, carpet underlay, shoes and furniture, demonstrating the material\'s safety when used as insulation. This widespread use across consumer products validates its safety profile.',
            'notes': 'Enhanced extraction: Safety validation through common product usage'
        },
        {
            'category': 'Cost & Value',
            'subcategory': 'Lifetime performance guarantee',
            'context_keywords': 'lifetime performance, building life guarantee, no degradation, maintained R-value',
            'answer': 'Unlike traditional insulation that can degrade, sag, or settle over time, Yetifoam maintains its full performance for the life of the building. This lifetime guarantee means no replacement costs or performance degradation, providing long-term value.',
            'notes': 'Enhanced extraction: Long-term value proposition with lifetime guarantee'
        },
        {
            'category': 'Installation & Application',
            'subcategory': 'Exothermic curing process benefits',
            'context_keywords': 'exothermic curing, heat generation, moisture expulsion, chemical reaction',
            'answer': 'During curing, the exothermic reaction generates heat that drives out residual moisture from the substrate, ensuring optimal adhesion and preventing moisture entrapment. This chemical process enhances the effectiveness of the moisture barrier.',
            'notes': 'Enhanced extraction: Technical curing process advantages'
        },
        {
            'category': 'Installation & Application',
            'subcategory': 'Site assessment recommendations',
            'context_keywords': 'site assessment, high-moisture environments, professional evaluation, optimal results',
            'answer': 'For optimal results in high-moisture environments or complex installations, a professional site assessment is recommended. This ensures proper substrate preparation and identifies any site-specific considerations for successful installation.',
            'notes': 'Enhanced extraction: Professional assessment value for complex projects'
        },
        {
            'category': 'Fire Safety & Compliance',
            'subcategory': 'PVC cable compatibility vs EPS issues',
            'context_keywords': 'PVC cable compatibility, EPS polystyrene issues, plasticizer migration, material differences',
            'answer': 'Because YetiFoam is polyurethane-based, it does not react with PVC cables. Issues such as plasticizer migration that affect cables occur with EPS polystyrene products, not with polyurethane-based YetiFoam, making it safe for electrical installations.',
            'notes': 'Enhanced extraction: Material chemistry differences for electrical safety'
        },
        {
            'category': 'Moisture Resistance',
            'subcategory': 'Calibrated moisture meter testing protocol',
            'context_keywords': 'calibrated moisture meters, 19% threshold, substrate testing, installation postponement',
            'answer': 'Professional applicators use calibrated moisture meters to test substrate dryness before installation. If moisture levels exceed 19%, installation is postponed until the substrate is adequately dry, ensuring proper adhesion and preventing moisture issues.',
            'notes': 'Enhanced extraction: Specific moisture testing protocol with threshold'
        },
        {
            'category': 'Installation & Application',
            'subcategory': 'Victorian manufacturing for Australian conditions',
            'context_keywords': 'Victorian manufacturing, Australian conditions, local climate, regional design',
            'answer': 'YetiFoam is made by Victorians for Victorians and is specifically designed for Australian conditions and climate. This local manufacturing ensures the product is optimized for regional building requirements and environmental factors.',
            'notes': 'Enhanced extraction: Local manufacturing advantages for climate suitability'
        }
    ]
    
    print(f"Adding {len(unique_entries)} new unique entries...")
    
    # Create DataFrame and combine
    new_df = pd.DataFrame(unique_entries)
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Save updated files
    updated_df.to_parquet('updated_final_unified_responses.parquet')
    updated_df.to_csv('updated_final_yetifoam_responses.csv', index=False)
    
    print(f"Updated dataset saved with {len(updated_df)} total rows ({len(unique_entries)} added)")
    
    # Show sample of new entries
    print("\nSample of new entries:")
    for i, entry in enumerate(unique_entries[:3]):
        print(f"Entry {i+1}: {entry['category']} - {entry['subcategory']}")
    
    return {
        'rows_added': len(unique_entries),
        'total_rows': len(updated_df),
        'issues': []
    }

if __name__ == "__main__":
    result = add_unique_responses()
    print(f"\nFinal result: {result}")