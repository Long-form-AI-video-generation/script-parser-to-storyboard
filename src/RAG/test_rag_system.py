"""
Simple test script for the basic RAG system

Tests core functionality with a sample anime script.
"""

import os
import sys
from pathlib import Path
from rag_system import AnimeScriptRAG
from rag_integration import RAGPromptGenerator


def create_sample_script():
    """Create a sample anime script for testing."""
    sample_script = """
ANIME SCRIPT - "The Last Guardian"

SCENE 1
INT. KENJI'S APARTMENT - NIGHT

The room is dimly lit by a single desk lamp. KENJI, a 17-year-old high school student, sits at his computer, typing furiously. His eyes are tired but determined.

KENJI: (muttering) I need to find it before they do.

He opens a new browser tab and searches for "ancient guardian artifacts". The screen flickers with search results.

ACTION: Close-up on Kenji's face as he reads the results. His expression changes from hope to disappointment.

KENJI: Nothing... but I know it's out there somewhere.

SCENE 2
EXT. SCHOOL COURTYARD - DAY

The next morning. Students are walking to class. Kenji approaches his best friend, YUKI, who is sitting on a bench reading a book.

KENJI: Yuki, I need your help with something.

YUKI: (looking up from book) What is it this time? Another one of your "mysterious quests"?

KENJI: This is different. I found something in my grandfather's old journal. There's a mention of a guardian spirit that protects our town.

YUKI: (skeptical) Kenji, you know I don't believe in that supernatural stuff.

KENJI: But what if it's real? What if there's something out there that needs our help?

ACTION: Yuki closes her book and looks at Kenji with concern.

YUKI: You're really serious about this, aren't you?

KENJI: I've never been more serious about anything in my life.

SCENE 3
INT. ABANDONED SHRINE - EVENING

Kenji and Yuki approach an old, crumbling shrine hidden in the forest. The atmosphere is eerie but peaceful.

YUKI: (whispering) This place gives me the creeps.

KENJI: (excited) This is it! This is where the guardian is supposed to be.

They enter the shrine. Inside, there's an ancient altar with strange symbols carved into it.

ACTION: Camera pans across the altar, revealing intricate carvings that seem to glow faintly.

KENJI: Look at these symbols. They're exactly like the ones in grandfather's journal.

YUKI: (touching the altar) They're warm... like they're alive.

Suddenly, a soft light begins to emanate from the altar. A gentle voice echoes through the shrine.

GUARDIAN SPIRIT: (ethereal voice) You have come seeking the truth, young ones.

KENJI: (amazed) It's real... it's really real!

YUKI: (in awe) I can't believe it...

GUARDIAN SPIRIT: The town faces a great danger. Only those with pure hearts can help protect it.

KENJI: We want to help! Tell us what we need to do.

The light intensifies, and the guardian spirit materializes as a beautiful, ethereal figure.

GUARDIAN SPIRIT: You must find the three sacred crystals hidden throughout the town. Only together can they restore the protective barrier.

YUKI: Where do we start looking?

GUARDIAN SPIRIT: The crystals will reveal themselves to those who are worthy. Trust your instincts and follow your hearts.

The spirit begins to fade, but the warmth remains.

KENJI: (determined) We'll find them. We'll protect our town.

YUKI: (nodding) Together.

FADE OUT.

END OF SCRIPT
"""
    
    # Create a simple text file that can be used as a "PDF" for testing
    sample_path = Path("sample_anime_script.txt")
    with open(sample_path, 'w', encoding='utf-8') as f:
        f.write(sample_script)
    
    return sample_path


def test_rag_system():
    """Test the RAG system functionality."""
    print("🧪 Testing RAG System")
    print("=" * 30)
    
    # Create sample script
    print("📝 Creating sample anime script...")
    sample_script_path = create_sample_script()
    print(f"✅ Sample script created: {sample_script_path}")
    
    # Initialize RAG system
    print("\n🔧 Initializing RAG system...")
    rag = AnimeScriptRAG(chunk_size=200, chunk_overlap=20)  # Smaller chunks for testing
    print("✅ RAG system initialized")
    
    # Add sample script to RAG
    print(f"\n📚 Adding sample script to RAG database...")
    success = rag.add_pdf_to_rag(str(sample_script_path), "sample_anime_script")
    if success:
        print("✅ Sample script added to RAG database")
    else:
        print("❌ Failed to add sample script to RAG database")
        return False
    
    # Test queries
    test_queries = [
        "Kenji searching for guardian artifacts",
        "Yuki and Kenji at the shrine",
        "guardian spirit appearance",
        "sacred crystals quest",
        "protecting the town"
    ]
    
    print("\n🔍 Testing RAG queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: '{query}'")
        
        results = rag.retrieve_relevant_context(query, top_k=3)
        if results:
            print(f"✅ Found {len(results)} relevant results:")
            for j, result in enumerate(results, 1):
                print(f"  {j}. [{result['similarity_score']:.3f}] {result['text'][:80]}...")
        else:
            print("❌ No results found")
    
    # Test RAG integration
    print("\n🔗 Testing RAG integration...")
    generator = RAGPromptGenerator()
    
    test_prompt = "Generate a video of Kenji and Yuki discovering the guardian spirit"
    enhanced_prompt = generator.enhance_video_generation_prompt(test_prompt)
    
    print("✅ Enhanced prompt generated:")
    print("-" * 40)
    print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)
    
    # Show database info
    print("\n📊 Database Information:")
    info = rag.get_database_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up sample file...")
    if sample_script_path.exists():
        sample_script_path.unlink()
        print("✅ Sample file cleaned up")
    
    print("\n🎉 RAG system test completed successfully!")
    return True


def test_storyboard_enhancement():
    """Test storyboard enhancement with RAG."""
    print("\n🎬 Testing Storyboard Enhancement")
    print("=" * 35)
    
    # Create a sample storyboard
    sample_storyboard = """
PANEL 001
SHOT_TYPE: CLOSE UP
SUBJECT: Kenji
ACTION_DESCRIPTION: Kenji sits at his computer, typing with determination. His tired eyes reflect the glow of the screen.
DIALOGUE: I need to find it before they do.

--- PANEL BREAK ---

PANEL 002
SHOT_TYPE: MEDIUM SHOT
SUBJECT: Kenji and Yuki
ACTION_DESCRIPTION: Kenji approaches Yuki who is reading on a bench. The school courtyard is bustling with students.
DIALOGUE: Yuki, I need your help with something.
"""
    
    # Save sample storyboard
    storyboard_path = Path("sample_storyboard.txt")
    with open(storyboard_path, 'w', encoding='utf-8') as f:
        f.write(sample_storyboard)
    
    try:
        # Test enhancement
        generator = RAGPromptGenerator()
        enhanced_path = generator.process_storyboard_file(str(storyboard_path))
        
        print(f"✅ Enhanced storyboard saved to: {enhanced_path}")
        
        # Show a preview of the enhanced content
        with open(enhanced_path, 'r', encoding='utf-8') as f:
            enhanced_content = f.read()
        
        print("\n📖 Enhanced Storyboard Preview:")
        print("-" * 40)
        print(enhanced_content[:800] + "..." if len(enhanced_content) > 800 else enhanced_content)
        
        # Cleanup
        storyboard_path.unlink()
        Path(enhanced_path).unlink()
        print("\n✅ Test files cleaned up")
        
    except Exception as e:
        print(f"❌ Error testing storyboard enhancement: {e}")
        if storyboard_path.exists():
            storyboard_path.unlink()


if __name__ == "__main__":
    print("🚀 Starting RAG System Tests")
    print("=" * 40)
    
    try:
        # Test basic RAG functionality
        success = test_rag_system()
        
        if success:
            # Test storyboard enhancement
            test_storyboard_enhancement()
        
        print("\n🎯 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
