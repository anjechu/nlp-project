#!/usr/bin/env python3
"""
Simple script to generate example TSV files for Google Embedding Projector.
This creates sample data without requiring the full NLP pipeline.
"""

import os

def create_sample_projector_files(output_dir="projector_output"):
    """
    Create sample vectors.tsv and metadata.tsv files for testing.
    These files can be uploaded to https://projector.tensorflow.org/
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample data - simulating 384-dimensional embeddings
    sample_texts = [
        "This game is amazing!",
        "这个游戏很好玩",
        "このゲームは素晴らしい",
        "Great graphics and gameplay",
        "性能问题需要改进",
        "バグが多すぎる",
        "Love the story and characters",
        "推荐给所有玩家",
        "音楽が最高です"
    ]
    
    # Language detection function
    def detect_language(text):
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return 'Chinese'
        elif any('\u3040' <= c <= '\u30ff' or '\u31f0' <= c <= '\u31ff' for c in text):
            return 'Japanese'
        else:
            return 'English'
    
    # Topic IDs
    topic_ids = [1, 1, 1, 2, 3, 3, 4, 1, 5]
    
    # Generate sample 384-dimensional embeddings (simplified for demo)
    import random
    random.seed(42)
    
    vectors_path = os.path.join(output_dir, "vectors.tsv")
    metadata_path = os.path.join(output_dir, "metadata.tsv")
    
    # Write vectors.tsv (no header)
    print(f"📊 Generating {vectors_path}...")
    with open(vectors_path, 'w', encoding='utf-8') as f:
        for i in range(len(sample_texts)):
            # Create a simple 384-dimensional vector (random for demo)
            # In real usage, these would be actual embeddings
            vector = [random.random() * 2 - 1 for _ in range(384)]
            line = '\t'.join(f"{v:.8f}" for v in vector)
            f.write(line + '\n')
    
    print(f"✅ Generated vectors.tsv with {len(sample_texts)} samples × 384 dimensions")
    
    # Write metadata.tsv (with header)
    print(f"📊 Generating {metadata_path}...")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        # Header
        f.write("text\ttopic_id\tlanguage\n")
        
        # Data rows
        for text, topic_id in zip(sample_texts, topic_ids):
            # Clean text (remove tabs and newlines)
            clean_text = text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
            language = detect_language(text)
            f.write(f"{clean_text}\t{topic_id}\t{language}\n")
    
    print(f"✅ Generated metadata.tsv with columns: text, topic_id, language")
    
    # Print language distribution
    languages = [detect_language(text) for text in sample_texts]
    from collections import Counter
    lang_counts = Counter(languages)
    print(f"\n📈 Language distribution:")
    for lang, count in lang_counts.items():
        print(f"   • {lang}: {count} samples")
    
    # Print instructions
    print(f"\n" + "="*60)
    print("✅ SUCCESS! Files generated in:", os.path.abspath(output_dir))
    print("="*60)
    print("\n📌 How to use with Google Embedding Projector:")
    print("   1. Go to: https://projector.tensorflow.org/")
    print("   2. Click 'Load' button (top left)")
    print("   3. Upload vectors.tsv first")
    print("   4. Upload metadata.tsv second")
    print("   5. Explore with PCA, t-SNE, or UMAP")
    print("   6. Color by 'language' or 'topic_id' in the sidebar")
    print("\n🎨 Tip: Try coloring by 'language' to see language clusters!")
    print("="*60)
    
    return {
        'vectors_path': vectors_path,
        'metadata_path': metadata_path,
        'num_samples': len(sample_texts),
        'num_dimensions': 384,
        'languages': dict(lang_counts)
    }

if __name__ == "__main__":
    print("🚀 Creating sample files for Google Embedding Projector...\n")
    result = create_sample_projector_files()
    print(f"\n✨ Done! Generated {result['num_samples']} samples with {result['num_dimensions']} dimensions.")
