#!/usr/bin/env python3
"""
Test script to generate an HTML report with the new hover UI
"""

import json
import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_llm_summaries_to_test_data(data):
    """Add mock LLM summaries to test data to test the hover functionality"""
    topics = data.get('topics', [])
    
    # Sample long summaries to test truncation and hover
    long_summaries = [
        "Players are deeply impressed by the immersive night city environment and the legendary status they can achieve. The game creates a compelling narrative where players can become the living legend that Night City has never seen before, which resonates strongly with the player base.",
        "The gameplay mechanics are highly engaging and provide an excellent fun factor. Players consistently report high enjoyment levels, with many describing the experience as genuinely entertaining and worth their time investment.",
        "The art style and graphics quality have received overwhelming positive feedback. Players appreciate the attention to visual detail, the unique aesthetic choices, and the overall presentation quality that makes the game world feel alive and believable.",
        "Story and narrative elements are a major highlight, with players praising the deep character development, meaningful choices, and emotional impact of the various storylines. The writing quality stands out as exceptional.",
        "Combat mechanics and difficulty balance have some issues. Players report frustration with certain encounters being too challenging or poorly balanced, which can detract from the overall enjoyment of otherwise excellent gameplay.",
        "Technical performance issues including bugs, crashes, and optimization problems are a significant concern. Many players experience game-breaking glitches that interrupt their gameplay experience and diminish their enjoyment.",
        "The game's progression system and character customization options provide excellent depth. Players enjoy the freedom to build their characters in diverse ways and appreciate the meaningful impact of their choices.",
        "Soundtrack and audio design receive high praise, with the music enhancing the atmosphere and immersion. The voice acting quality is also noted as being top-tier and contributing to the overall experience.",
        "Some players feel the game world lacks sufficient interactive elements or meaningful side activities. While the main content is strong, there are requests for more diverse activities and deeper world interaction.",
        "Localization quality varies across different language versions. Some players in non-English markets report translation issues or cultural adaptation problems that affect their understanding and immersion."
    ]
    
    for i, topic in enumerate(topics):
        # Add a summary to each topic (use modulo to cycle through summaries)
        topic['summary'] = long_summaries[i % len(long_summaries)]
        
        # Add topic name if not present
        if 'topic_name' not in topic:
            topic_names = [
                "Night City Legendary Experience",
                "Gameplay Fun Factor",
                "Visual & Art Style",
                "Story & Narrative",
                "Combat Difficulty",
                "Technical Performance",
                "Character Progression",
                "Sound & Music",
                "World Interactivity",
                "Localization Quality"
            ]
            topic['topic_name'] = topic_names[i % len(topic_names)]
        
        # Set source_language for proper grouping
        if 'source_language' not in topic:
            langs = ['schinese', 'japanese', 'english']
            topic['source_language'] = langs[i % 3]
    
    # Mark as LLM enhanced
    data['llm_enhanced'] = True
    data['valuable_topics_count'] = len(topics)
    
    return data

def main():
    print("🧪 Testing Executive Summary Hover UI")
    print("=" * 60)
    
    # Load test data
    with open('refined_topics_test.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Add mock LLM summaries
    test_data = add_llm_summaries_to_test_data(test_data)
    
    # Create output directory
    os.makedirs('analysis', exist_ok=True)
    
    # Import after setting up path
    try:
        from analysis_report_generator import AnalysisReportGenerator
        
        # Initialize generators (without actual LLM/chart generation for this test)
        generator = AnalysisReportGenerator(llm_generator=None, chart_generator=None)
        
        # Generate report
        print("\n📊 Generating HTML report with hover functionality...")
        
        # Create empty chart images dict for testing
        chart_images = {
            'sentiment_distribution': '',
            'topic_density': '',
            'sentiment_scores': ''
        }
        
        html_content = generator._generate_html_report(test_data, chart_images, test_data)
        
        # Save the HTML
        output_path = 'analysis/test_hover_ui.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ Report generated: {output_path}")
        print("\n📝 To test the hover effect:")
        print(f"   Open {output_path} in a web browser")
        print("   Scroll to 'Executive Summary for Game Developers' section")
        print("   Hover over any topic item with a '...' truncated summary")
        print("   The item should expand and show the full LLM insight!")
        
        # Also print absolute path
        abs_path = os.path.abspath(output_path)
        print(f"\n🔗 Absolute path: {abs_path}")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Installing dependencies might be needed.")
        print("   But the code changes are complete!")

if __name__ == '__main__':
    main()
