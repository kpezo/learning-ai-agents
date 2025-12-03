"""Quick test to verify topic extraction works."""

from adk.quiz_tools import _extract_topics_from_pdf

# Test topic extraction
result = _extract_topics_from_pdf(max_topics=10)

print("Topic Extraction Test")
print("=" * 70)

if result["status"] == "success":
    print(f"✓ Successfully extracted {len(result['topics'])} topics")
    print(f"  Total passages analyzed: {result['total_passages']}")
    print(f"  Message: {result['message']}")
    print("\nExtracted Topics:")
    for i, topic in enumerate(result["topics"], 1):
        print(f"  {i}. {topic['name']} (frequency: {topic['frequency']}, relevance: {topic['relevance_score']:.2f})")
else:
    print(f"✗ Error: {result['error_message']}")

print("=" * 70)
