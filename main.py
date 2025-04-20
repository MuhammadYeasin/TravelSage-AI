import os
import argparse

def main():
    """
    Main entry point for the Travel Assistant application.
    Allows selecting between CLI mode and web frontend.
    """
    parser = argparse.ArgumentParser(description="Personal Travel Assistant")
    parser.add_argument("--mode", choices=["cli", "web"], default="web",
                      help="Mode to run the assistant (cli or web)")
    parser.add_argument("--test-llm", action="store_true",
                      help="Run LLM tests before starting")
    
    args = parser.parse_args()
    
    # Run LLM tests if requested
    if args.test_llm:
        print("Testing LLM configurations...")
        from llm_setup import test_travel_prompts
        test_travel_prompts()
    
    # Launch the appropriate interface
    if args.mode == "cli":
        print("Starting CLI interface...")
        from dialogue_system import run_cli_dialogue
        run_cli_dialogue()
    else:
        print("Starting web interface. Please wait...")
        # We use os.system because streamlit needs to be run as a separate process
        os.system("streamlit run frontend.py")

if __name__ == "__main__":
    main()