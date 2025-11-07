"""
Demo Test Script

This script tests the RAG chatbot with prepared demo questions.
Use this to verify everything works before the presentation.
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List

# API endpoint
API_URL = "http://localhost:8000/api/v1/chat"
HEALTH_URL = "http://localhost:8000/api/v1/health/detailed"


def check_health() -> bool:
    """Check if the API server is healthy."""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("✅ API Server: Healthy")
            print(f"   - Vector DB: {health['components'].get('vector_db', 'unknown')}")
            print(f"   - LLM Service: {health['components'].get('llm_service', 'unknown')}")
            if 'llm_model' in health['components']:
                print(f"   - Model: {health['components']['llm_model']}")
            return True
        else:
            print(f"❌ API Server: Unhealthy (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API Server: Not running. Please start the server with 'python main.py'")
        return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False


def test_query(question: str, expected_topic: str = None) -> Dict:
    """
    Test a single query.
    
    Args:
        question: The question to ask
        expected_topic: Expected topic (for validation)
        
    Returns:
        Dict: Response from API
    """
    try:
        print(f"\n📝 Question: {question}")
        if expected_topic:
            print(f"   Expected topic: {expected_topic}")
        
        start_time = time.time()
        response = requests.post(
            API_URL,
            json={"message": question},
            timeout=30
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            
            print(f"✅ Response received ({elapsed_time:.2f}s)")
            print(f"   Answer: {answer[:200]}..." if len(answer) > 200 else f"   Answer: {answer}")
            print(f"   Sources: {len(sources)}")
            for i, source in enumerate(sources[:3], 1):  # Show first 3 sources
                url = source.get("url", "N/A")
                print(f"      {i}. {url[:80]}...")
            
            return {
                "success": True,
                "question": question,
                "answer": answer,
                "sources": sources,
                "response_time": elapsed_time
            }
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   {response.text}")
            return {
                "success": False,
                "question": question,
                "error": response.text
            }
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out (>30s)")
        return {"success": False, "question": question, "error": "Timeout"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "question": question, "error": str(e)}


def run_demo_tests():
    """Run all demo questions."""
    print("=" * 80)
    print("KSU IT RAG Chatbot - Demo Test Script")
    print("=" * 80)
    
    # Check health first
    print("\n🔍 Checking API health...")
    if not check_health():
        print("\n❌ Cannot proceed. Please ensure the API server is running.")
        return
    
    # Load demo questions
    demo_file = Path(__file__).parent.parent / "demo_questions.json"
    if not demo_file.exists():
        print(f"\n❌ Demo questions file not found: {demo_file}")
        return
    
    with open(demo_file, 'r') as f:
        demo_data = json.load(f)
    
    questions = sorted(
        demo_data["demo_questions"],
        key=lambda x: x.get("demo_order", 999)
    )
    
    print(f"\n📋 Testing {len(questions)} demo questions...")
    print("=" * 80)
    
    results = []
    for q in questions:
        result = test_query(
            q["question"],
            q.get("expected_topic")
        )
        results.append(result)
        time.sleep(1)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    
    successful = sum(1 for r in results if r.get("success"))
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful > 0:
        avg_time = sum(r.get("response_time", 0) for r in results if r.get("success")) / successful
        print(f"⏱️  Average response time: {avg_time:.2f}s")
    
    # Save results
    results_file = Path(__file__).parent.parent / "demo_test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_questions": total,
            "successful": successful,
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    if successful == total:
        print("\n🎉 All tests passed! Ready for demo.")
    else:
        print(f"\n⚠️  {total - successful} test(s) failed. Review errors above.")


if __name__ == "__main__":
    run_demo_tests()

