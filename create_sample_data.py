#!/usr/bin/env python3
"""
Example script to create sample data for testing the NLP Comment Processor
"""

import json
import os

# Sample comments data
sample_data = {
    "comments": [
        {
            "id": 1,
            "text": "This product is absolutely amazing! I love it so much! Best purchase ever!",
            "user": "alice_123",
            "date": "2024-01-15"
        },
        {
            "id": 2,
            "text": "Terrible experience. Very disappointed with the quality. Waste of money.",
            "user": "bob_smith",
            "date": "2024-01-16"
        },
        {
            "id": 3,
            "text": "It's okay. Nothing special, but it works as expected.",
            "user": "charlie_99",
            "date": "2024-01-17"
        },
        {
            "id": 4,
            "text": "Great product! Highly recommended. Excellent quality and fast shipping!",
            "user": "diana_jones",
            "date": "2024-01-18"
        },
        {
            "id": 5,
            "text": "Awful and frustrating. Customer service was horrible.",
            "user": "eve_williams",
            "date": "2024-01-19"
        },
        {
            "id": 6,
            "text": "Good value for money. Happy with my purchase.",
            "user": "frank_miller",
            "date": "2024-01-20"
        },
        {
            "id": 7,
            "text": "The product broke after one week. Very disappointed and sad.",
            "user": "grace_lee",
            "date": "2024-01-21"
        },
        {
            "id": 8,
            "text": "Perfect! Exactly what I was looking for. Love the design!",
            "user": "henry_clark",
            "date": "2024-01-22"
        },
        {
            "id": 9,
            "text": "Not bad, not great. Just average.",
            "user": "iris_brown",
            "date": "2024-01-23"
        },
        {
            "id": 10,
            "text": "Fantastic product! Best in the market. Highly satisfied!",
            "user": "jack_white",
            "date": "2024-01-24"
        }
    ]
}

# Save to file
output_file = "sample_comments.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(sample_data, f, indent=2, ensure_ascii=False)

print(f"✓ Sample data created: {output_file}")
print(f"✓ Total comments: {len(sample_data['comments'])}")
print("\nYou can now use this file with the NLP Comment Processor GUI:")
print(f"  1. Run: python gui.py")
print(f"  2. Select '{output_file}' as the input file")
print(f"  3. Choose an output location")
print(f"  4. Click 'Process Comments'")
