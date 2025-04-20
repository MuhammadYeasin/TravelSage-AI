import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from dialogue_system import create_dialogue_stages, construct_travel_prompt, generate_travel_plan, compare_travel_plans, refine_travel_plan

# Set up the Streamlit app
st.set_page_config(
    page_title="Personal Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve appearance
st.markdown("""
<style>
    .main {
        padding: 20px;
    }
    .stButton>button {
        width: 100%;
    }
    .stTextArea>div>div>textarea {
        height: 150px;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .highlight {
        background-color: #f0f7ff;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'user_responses' not in st.session_state:
    st.session_state['user_responses'] = {}
if 'current_stage' not in st.session_state:
    st.session_state['current_stage'] = 0
if 'travel_plan' not in st.session_state:
    st.session_state['travel_plan'] = None
if 'comparison_mode' not in st.session_state:
    st.session_state['comparison_mode'] = False
if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = "openai"
if 'show_examples' not in st.session_state:
    st.session_state['show_examples'] = False

# Function to move to the next stage
def next_stage():
    st.session_state['current_stage'] += 1

# Function to move to the previous stage
def prev_stage():
    if st.session_state['current_stage'] > 0:
        st.session_state['current_stage'] -= 1

# Function to generate travel plan
def generate_plan():
    if st.session_state['comparison_mode']:
        plans = compare_travel_plans(st.session_state['user_responses'])
        st.session_state['travel_plan'] = plans
    else:
        model = st.session_state['selected_model']
        plan = generate_travel_plan(st.session_state['user_responses'], model)
        st.session_state['travel_plan'] = {model: plan}

# Function to reset the app
def reset_app():
    st.session_state['user_responses'] = {}
    st.session_state['current_stage'] = 0
    st.session_state['travel_plan'] = None
    st.session_state['comparison_mode'] = False
    st.session_state['selected_model'] = "openai"

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.title("✈️ Travel Assistant")
        st.markdown("---")
        
        # Example destinations
        st.subheader("Popular Destinations")
        if st.button("🇫🇷 Paris, France"):
            st.session_state['user_responses']['travel_destination'] = "Paris, France"
        if st.button("🇯🇵 Tokyo, Japan"):
            st.session_state['user_responses']['travel_destination'] = "Tokyo, Japan"
        if st.button("🇮🇹 Rome, Italy"):
            st.session_state['user_responses']['travel_destination'] = "Rome, Italy"
        if st.button("🇬🇷 Athens, Greece"):
            st.session_state['user_responses']['travel_destination'] = "Athens, Greece"
        
        st.markdown("---")
        
        # Show current progress
        if st.session_state['current_stage'] < len(create_dialogue_stages()):
            progress_percent = int((st.session_state['current_stage'] / len(create_dialogue_stages())) * 100)
            st.progress(progress_percent / 100)
            st.caption(f"Progress: {progress_percent}%")
        
        # Reset button
        if st.button("Start Over"):
            reset_app()
            st.experimental_rerun()

    # Main content
    st.title("Personal Travel Assistant")
    
    # Get dialogue stages
    dialogue_stages = create_dialogue_stages()
    
    # Display appropriate content based on current stage
    if st.session_state['current_stage'] < len(dialogue_stages):
        # Collection phase
        current_stage = dialogue_stages[st.session_state['current_stage']]
        
        # If it's the introduction stage, show welcome message
        if current_stage["name"] == "introduction":
            st.markdown("""
            <div class="highlight">
                <h2>Welcome to Your Personal Travel Assistant! 🌍</h2>
                <p>I'll help you plan the perfect trip based on your preferences. Let me ask you a few questions to get started.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Let's Get Started!"):
                next_stage()
                st.experimental_rerun()
        
        else:
            # Show input fields for other stages
            st.subheader(f"Step {st.session_state['current_stage']} of {len(dialogue_stages)-1}")
            st.write(current_stage["prompt"])
            
            # Show examples toggle
            show_examples = st.checkbox("Show me examples", value=st.session_state['show_examples'])
            st.session_state['show_examples'] = show_examples
            
            # Display examples if requested
            if show_examples:
                if current_stage["name"] == "personal_info":
                    st.info("Example: My name is Alex, I'm 32 years old, and I'll be traveling with my partner.")
                elif current_stage["name"] == "travel_destination":
                    st.info("Example: I'd like to visit Barcelona, Spain.")
                elif current_stage["name"] == "travel_dates":
                    st.info("Example: Planning to travel for 10 days in August 2025.")
                elif current_stage["name"] == "budget":
                    st.info("Example: My budget is around $3000 for the entire trip excluding flights.")
                elif current_stage["name"] == "interests":
                    st.info("Example: I'm interested in historical sites, local cuisine, and beach activities.")
            
            # Get user input
            prev_response = st.session_state['user_responses'].get(current_stage["name"], "")
            user_input = st.text_area("Your response:", value=prev_response)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state['current_stage'] > 1:  # Skip back button on first non-intro stage
                    if st.button("← Back"):
                        prev_stage()
                        st.experimental_rerun()
            
            with col2:
                if st.button("Continue →"):
                    if current_stage["required"] and not user_input.strip():
                        st.error("This information is required to continue.")
                    else:
                        st.session_state['user_responses'][current_stage["name"]] = user_input
                        next_stage()
                        st.experimental_rerun()
    
    elif st.session_state['current_stage'] == len(dialogue_stages):
        # Model selection phase
        st.subheader("Create Your Travel Plan")
        
        # Display summary of collected information
        st.markdown("### Your Travel Preferences")
        for key, value in st.session_state['user_responses'].items():
            if key != "introduction" and value.strip():
                st.write(f"**{key.replace('_', ' ').title()}**: {value}")
        
        st.markdown("---")
        
        # Model selection options
        st.subheader("Choose Your AI Travel Planner")
        
        comparison = st.checkbox("Compare both AI models", value=False)
        st.session_state['comparison_mode'] = comparison
        
        if not comparison:
            model = st.radio("Select a model for your travel plan:", 
                            ["OpenAI (More concise)", "Llama (More detailed)"],
                            captions=["Generates shorter, focused plans", "Creates detailed, comprehensive itineraries"])
            
            st.session_state['selected_model'] = "openai" if "OpenAI" in model else "llama"
        
        # Generate plan button
        if st.button("Generate My Travel Plan"):
            with st.spinner("Creating your personalized travel itinerary..."):
                generate_plan()
            next_stage()
            st.experimental_rerun()
    
    else:
        # Display travel plan phase
        st.subheader("Your Personalized Travel Plan")
        
        if st.session_state['comparison_mode']:
            # Show comparison tabs
            tab1, tab2 = st.tabs(["OpenAI Plan", "Llama Plan"])
            
            with tab1:
                st.markdown(st.session_state['travel_plan'].get("OpenAI", "Plan not available"))
                if st.button("Choose OpenAI Plan"):
                    st.session_state['travel_plan'] = {"openai": st.session_state['travel_plan'].get("OpenAI", "")}
                    st.session_state['comparison_mode'] = False
                    st.session_state['selected_model'] = "openai"
                    st.experimental_rerun()
            
            with tab2:
                st.markdown(st.session_state['travel_plan'].get("Llama 3.2", "Plan not available"))
                if st.button("Choose Llama Plan"):
                    st.session_state['travel_plan'] = {"llama": st.session_state['travel_plan'].get("Llama 3.2", "")}
                    st.session_state['comparison_mode'] = False
                    st.session_state['selected_model'] = "llama"
                    st.experimental_rerun()
        
        else:
            # Show selected plan
            selected_model = next(iter(st.session_state['travel_plan']))
            plan_text = st.session_state['travel_plan'][selected_model]
            
            st.markdown(plan_text)
            
            # Export options
            st.download_button(
                label="Export Plan as Text",
                data=plan_text,
                file_name="travel_plan.txt",
                mime="text/plain"
            )
        
        # Refinement options
        st.markdown("---")
        st.subheader("Refine Your Plan")
        
        refinement = st.text_area("What would you like to change or add to your plan?", 
                                placeholder="Example: Add more family-friendly activities, include budget dining options, add a day trip to a nearby city...")
        
        if st.button("Refine My Plan"):
            with st.spinner("Refining your travel plan..."):
                if st.session_state['comparison_mode']:
                    # If in comparison mode, refine both plans
                    refined_openai = refine_travel_plan(
                        st.session_state['travel_plan'].get("OpenAI", ""),
                        refinement,
                        "openai"
                    )
                    
                    refined_llama = refine_travel_plan(
                        st.session_state['travel_plan'].get("Llama 3.2", ""),
                        refinement,
                        "llama"
                    )
                    
                    st.session_state['travel_plan'] = {
                        "OpenAI": refined_openai,
                        "Llama 3.2": refined_llama
                    }
                else:
                    # Refine only the selected plan
                    selected_model = next(iter(st.session_state['travel_plan']))
                    model_type = "openai" if selected_model == "openai" or selected_model == "OpenAI" else "llama"
                    
                    refined_plan = refine_travel_plan(
                        st.session_state['travel_plan'][selected_model],
                        refinement,
                        model_type
                    )
                    
                    st.session_state['travel_plan'] = {selected_model: refined_plan}
                
            st.experimental_rerun()
        
        # Start over button
        if st.button("Create A New Trip Plan"):
            reset_app()
            st.experimental_rerun()

# Run the Streamlit app
if __name__ == "__main__":
    main()