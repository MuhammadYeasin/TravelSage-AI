import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import time
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
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stTextArea>div>div>textarea {
        height: 150px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .highlight {
        background-color: #f0f7ff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #1E88E5;
    }
    .destination-card {
        padding: 15px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .destination-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .progress-container {
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .footer {
        margin-top: 50px;
        text-align: center;
        color: #666;
        font-size: 0.8em;
    }
    /* Theme toggle styles */
    .dark-mode {
        background-color: #262730;
        color: #f1f1f1;
    }
    .light-mode {
        background-color: #ffffff;
        color: #262730;
    }
    /* Animated loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .loading-animation {
        animation: pulse 1.5s infinite;
        background-color: #f0f7ff;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
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
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False
if 'feedback' not in st.session_state:
    st.session_state['feedback'] = {}

# Function to move to the next stage
def next_stage():
    st.session_state['current_stage'] += 1

# Function to move to the previous stage
def prev_stage():
    if st.session_state['current_stage'] > 0:
        st.session_state['current_stage'] -= 1

# Function to generate travel plan with simulated loading
def generate_plan():
    with st.spinner("Creating your personalized travel itinerary..."):
        # Simulate processing time for better UX
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)  # Adjust for desired loading time
            progress_bar.progress(i + 1)
            
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
    # Keep feedback data

# Function to toggle dark mode
def toggle_theme():
    st.session_state['dark_mode'] = not st.session_state['dark_mode']

# Function to submit feedback
def submit_feedback(rating, comment):
    st.session_state['feedback'] = {
        'rating': rating,
        'comment': comment,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return st.success("Thank you for your feedback! We appreciate your input.")

# Render destination card
def destination_card(emoji, name, description):
    html = f"""
    <div class="destination-card" onclick="alert('Selected {name}!')">
        <h3>{emoji} {name}</h3>
        <p>{description}</p>
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

# Popular destinations with brief descriptions
destinations = [
    {"emoji": "🇫🇷", "name": "Paris, France", "description": "The city of lights, romance, and exquisite cuisine."},
    {"emoji": "🇯🇵", "name": "Tokyo, Japan", "description": "A vibrant metropolis blending ultramodern and traditional."},
    {"emoji": "🇮🇹", "name": "Rome, Italy", "description": "Ancient history and world-class art in every corner."},
    {"emoji": "🇬🇷", "name": "Athens, Greece", "description": "The cradle of Western civilization with stunning ruins."},
    {"emoji": "🇹🇭", "name": "Bangkok, Thailand", "description": "Vibrant street life and ornate shrines in Southeast Asia."},
    {"emoji": "🇲🇽", "name": "Mexico City, Mexico", "description": "Rich culture, amazing food, and ancient pyramids nearby."}
]

# Main app
def main():
    # Apply theme if dark mode is enabled
    if st.session_state['dark_mode']:
        st.markdown("""
        <style>
        .main, .css-1d391kg, .css-12oz5g7 {
            background-color: #262730;
            color: #f1f1f1;
        }
        .highlight, .card {
            background-color: #3b3b4f;
            color: #f1f1f1;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("✈️ Travel Assistant")
        st.markdown("---")
        
        # Theme toggle
        theme_label = "🌙 Switch to Light Mode" if st.session_state['dark_mode'] else "🌞 Switch to Dark Mode"
        if st.button(theme_label):
            toggle_theme()
            st.experimental_rerun()
        
        st.markdown("---")
        
        # Popular Destinations section
        st.subheader("Popular Destinations")
        
        # More visually appealing destination selection
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"{destinations[0]['emoji']} {destinations[0]['name']}", help=destinations[0]['description']):
                st.session_state['user_responses']['travel_destination'] = destinations[0]['name']
            
            if st.button(f"{destinations[2]['emoji']} {destinations[2]['name']}", help=destinations[2]['description']):
                st.session_state['user_responses']['travel_destination'] = destinations[2]['name']
            
            if st.button(f"{destinations[4]['emoji']} {destinations[4]['name']}", help=destinations[4]['description']):
                st.session_state['user_responses']['travel_destination'] = destinations[4]['name']
        
        with col2:
            if st.button(f"{destinations[1]['emoji']} {destinations[1]['name']}", help=destinations[1]['description']):
                st.session_state['user_responses']['travel_destination'] = destinations[1]['name']
            
            if st.button(f"{destinations[3]['emoji']} {destinations[3]['name']}", help=destinations[3]['description']):
                st.session_state['user_responses']['travel_destination'] = destinations[3]['name']
            
            if st.button(f"{destinations[5]['emoji']} {destinations[5]['name']}", help=destinations[5]['description']):
                st.session_state['user_responses']['travel_destination'] = destinations[5]['name']
        
        st.markdown("---")
        
        # Show current progress
        if st.session_state['current_stage'] < len(create_dialogue_stages()):
            progress_percent = int((st.session_state['current_stage'] / len(create_dialogue_stages())) * 100)
            st.markdown(f"### Planning Progress: {progress_percent}%")
            st.progress(progress_percent / 100)
        
        # Reset button
        if st.button("🔄 Start Over"):
            reset_app()
            st.experimental_rerun()
        
        # Help & FAQ accordion
        with st.expander("❓ Help & FAQ"):
            st.markdown("""
            **How does this work?**
            
            Our Travel Assistant uses AI to create personalized travel plans based on your preferences.
            
            **Is my data secure?**
            
            Yes, we don't store your personal information permanently.
            
            **Can I modify my plan after it's generated?**
            
            Absolutely! Once your plan is generated, you can refine it with specific requests.
            """)

    # Main content
    st.title("🌍 Personal Travel Assistant")
    
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
                <h2>✨ Welcome to Your Personal Travel Assistant! ✨</h2>
                <p>I'll help you plan the perfect trip based on your preferences. Let me ask you a few questions to understand what you're looking for in your ideal getaway.</p>
                <p>With just a few minutes of your time, I'll create a custom itinerary that matches your travel style, interests, and budget.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Showcase features
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="card">
                    <h3>🤖 AI-Powered</h3>
                    <p>Advanced AI technology creates personalized itineraries just for you.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="card">
                    <h3>💰 Budget-Friendly</h3>
                    <p>Get recommendations that respect your budget constraints.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="card">
                    <h3>🔄 Flexible Plans</h3>
                    <p>Easily refine and adjust your itinerary as needed.</p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🚀 Let's Get Started!"):
                next_stage()
                st.experimental_rerun()
        
        else:
            # Show input fields for other stages
            st.markdown(f"""
            <div class="highlight">
                <h2>Step {st.session_state['current_stage']} of {len(dialogue_stages)-1}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"### {current_stage['prompt']}")
            
            # Show examples toggle with a more subtle design
            show_examples = st.checkbox("💡 Show me examples", value=st.session_state['show_examples'])
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
                elif current_stage["name"] == "accommodation_preference":
                    st.info("Example: I prefer boutique hotels with character, ideally in central locations.")
                elif current_stage["name"] == "dietary_restrictions":
                    st.info("Example: I'm vegetarian and my partner has a gluten allergy.")
                elif current_stage["name"] == "additional_info":
                    st.info("Example: We'd like to avoid tourist traps and experience authentic local culture.")
            
            # Get user input with a more prominent design - create a unique key for each stage to prevent input persistence
            prev_response = st.session_state['user_responses'].get(current_stage["name"], "")
            user_input = st.text_area("Your response:", value=prev_response, 
                                     placeholder="Type your answer here...",
                                     key=f"input_{current_stage['name']}")
            
            # Navigation buttons with improved styling
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state['current_stage'] > 1:  # Skip back button on first non-intro stage
                    if st.button("⬅️ Back"):
                        prev_stage()
                        st.experimental_rerun()
            
            with col2:
                continue_button = st.button("Continue ➡️")
                if continue_button:
                    if current_stage["required"] and not user_input.strip():
                        st.error("⚠️ This information is required to continue. Please provide a response.")
                    else:
                        st.session_state['user_responses'][current_stage["name"]] = user_input
                        next_stage()
                        st.experimental_rerun()
    
    elif st.session_state['current_stage'] == len(dialogue_stages):
        # Model selection phase
        st.markdown("""
        <div class="highlight">
            <h2>🎯 Create Your Perfect Travel Plan</h2>
            <p>We've collected all your preferences. Now it's time to generate your personalized travel itinerary!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display summary of collected information in a card format
        st.markdown("### 📋 Your Travel Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>Personal Details</h3>
            """, unsafe_allow_html=True)
            
            if "personal_info" in st.session_state['user_responses']:
                st.write(f"**Who**: {st.session_state['user_responses']['personal_info']}")
            
            if "travel_destination" in st.session_state['user_responses']:
                st.write(f"**Destination**: {st.session_state['user_responses']['travel_destination']}")
            
            if "travel_dates" in st.session_state['user_responses']:
                st.write(f"**When**: {st.session_state['user_responses']['travel_dates']}")
            
            if "budget" in st.session_state['user_responses']:
                st.write(f"**Budget**: {st.session_state['user_responses']['budget']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>Preferences</h3>
            """, unsafe_allow_html=True)
            
            if "interests" in st.session_state['user_responses']:
                st.write(f"**Interests**: {st.session_state['user_responses']['interests']}")
            
            if "accommodation_preference" in st.session_state['user_responses']:
                st.write(f"**Accommodation**: {st.session_state['user_responses']['accommodation_preference']}")
            
            if "dietary_restrictions" in st.session_state['user_responses']:
                st.write(f"**Dietary Needs**: {st.session_state['user_responses']['dietary_restrictions']}")
            
            if "additional_info" in st.session_state['user_responses']:
                st.write(f"**Additional Info**: {st.session_state['user_responses']['additional_info']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Model selection options with more information
        st.markdown("""
        <div class="card">
            <h3>🤖 Choose Your AI Travel Planner</h3>
            <p>Select which AI model will create your travel plan. Each has different strengths!</p>
        </div>
        """, unsafe_allow_html=True)
        
        comparison = st.checkbox("🔍 Compare both AI models side by side", value=False, 
                               help="Generate plans from both models to compare approaches")
        st.session_state['comparison_mode'] = comparison
        
        if not comparison:
            model = st.radio("Select a model for your travel plan:", 
                            ["OpenAI (More concise)", "Llama (More detailed)"],
                            captions=["Generates shorter, focused plans with key highlights", 
                                    "Creates detailed, comprehensive itineraries with more suggestions"])
            
            st.session_state['selected_model'] = "openai" if "OpenAI" in model else "llama"
        
        # Generate plan button with animation
        if st.button("✨ Generate My Travel Plan"):
            generate_plan()
            next_stage()
            st.experimental_rerun()
    
    else:
        # Display travel plan phase with enhanced presentation
        st.markdown("""
        <div class="highlight">
            <h2>🎉 Your Personalized Travel Plan</h2>
            <p>Here's your custom travel itinerary based on your preferences!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state['comparison_mode']:
            # Show comparison tabs with enhanced design
            st.markdown("### Compare AI-Generated Travel Plans")
            st.write("Review both plans and choose the one you prefer.")
            
            tab1, tab2 = st.tabs(["📝 OpenAI Plan", "📋 Llama Plan"])
            
            with tab1:
                st.markdown("""
                <div class="card">
                    <h3>OpenAI-Generated Plan</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(st.session_state['travel_plan'].get("OpenAI", "Plan not available"))
                if st.button("✅ Choose OpenAI Plan"):
                    st.session_state['travel_plan'] = {"openai": st.session_state['travel_plan'].get("OpenAI", "")}
                    st.session_state['comparison_mode'] = False
                    st.session_state['selected_model'] = "openai"
                    st.experimental_rerun()
            
            with tab2:
                st.markdown("""
                <div class="card">
                    <h3>Llama-Generated Plan</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(st.session_state['travel_plan'].get("Llama 3.2", "Plan not available"))
                if st.button("✅ Choose Llama Plan"):
                    st.session_state['travel_plan'] = {"llama": st.session_state['travel_plan'].get("Llama 3.2", "")}
                    st.session_state['comparison_mode'] = False
                    st.session_state['selected_model'] = "llama"
                    st.experimental_rerun()
        
        else:
            # Show selected plan with better formatting
            selected_model = next(iter(st.session_state['travel_plan']))
            plan_text = st.session_state['travel_plan'][selected_model]
            
            st.markdown("""
            <div class="card">
                <h3>Your Custom Travel Itinerary</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(plan_text)
            
            # Export options with more choices
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Export Plan as Text",
                    data=plan_text,
                    file_name="travel_plan.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Export as formatted PDF (this would require additional backend implementation)
                st.button("📊 Export as PDF", disabled=True, help="PDF export coming soon!")
        
        # Refinement options with better guidance
        st.markdown("---")
        st.markdown("""
        <div class="card">
            <h3>✏️ Refine Your Plan</h3>
            <p>Want to adjust something? Tell us what you'd like to change, and we'll update your plan.</p>
        </div>
        """, unsafe_allow_html=True)
        
        refinement = st.text_area("What would you like to change or add to your plan?", 
                                placeholder="Examples:\n- Add more family-friendly activities\n- Include budget dining options\n- Add a day trip to a nearby city\n- Focus more on outdoor activities\n- Include local transportation options")
        
        if st.button("🔄 Refine My Plan"):
            with st.spinner("Refining your travel plan..."):
                # Simulate processing with progress bar
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
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
        
        # Feedback section
        st.markdown("---")
        st.markdown("""
        <div class="card">
            <h3>💬 Share Your Feedback</h3>
            <p>How was your experience? Your feedback helps us improve!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            rating = st.slider("Rate your experience:", 1, 5, 5)
        
        with col2:
            feedback_text = st.text_input("Comments or suggestions:", 
                                       placeholder="Tell us what you liked or how we can improve...")
        
        if st.button("📤 Submit Feedback"):
            submit_feedback(rating, feedback_text)
        
        # Display feedback success message if submitted
        if 'feedback' in st.session_state and st.session_state['feedback']:
            st.success("Thank you for your feedback! We appreciate your input.")
        
        # Start over button
        st.markdown("---")
        if st.button("🔄 Create A New Trip Plan"):
            reset_app()
            st.experimental_rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025 Personal Travel Assistant | Built with Streamlit | COMP8420 Assignment</p>
    </div>
    """, unsafe_allow_html=True)

# Run the Streamlit app
if __name__ == "__main__":
    main()