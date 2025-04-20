import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def query_openai_api(prompt, model="gpt-3.5-turbo"):
    """
    Function to query OpenAI's API with a prompt using the updated client.
    
    Args:
        prompt (str): The user prompt to send to the API
        model (str): The model to use for generation
    
    Returns:
        str: The model's response
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying OpenAI API: {str(e)}")
        return f"Error: {str(e)}"

def query_local_llama(prompt, model_name="llama3.2"):
    """
    Function to query local Llama 3.2 via Ollama with revised API handling.
    
    Args:
        prompt (str): The user prompt
        model_name (str): The name of your locally installed model
    
    Returns:
        str: The model's response
    """
    try:
        # Using Ollama API with streaming disabled
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            # Parse the response carefully
            result = response.json()
            if "response" in result:
                return result["response"]
            else:
                return f"Unexpected response format: {json.dumps(result)}"
        else:
            return f"Error: Status code {response.status_code}, {response.text}"
    except Exception as e:
        print(f"Error querying local Llama model: {str(e)}")
        return f"Error: {str(e)}"

def compare_models(prompt):
    """
    Compare responses from both models for the same prompt.
    
    Args:
        prompt (str): The prompt to send to both models
    
    Returns:
        dict: Dictionary with model responses
    """
    openai_response = query_openai_api(prompt)
    llama_response = query_local_llama(prompt)
    
    return {
        "OpenAI": openai_response,
        "Llama 3.2": llama_response
    }

def test_travel_prompts():
    """
    Function to test both LLM setups with various travel-related prompts.
    """
    # Set of travel-related test prompts
    test_prompts = [
        "What are the top 3 tourist attractions in Barcelona that are off the beaten path?",
        "Create a 3-day itinerary for Tokyo for a first-time visitor.",
        "What's the best time of year to visit New Zealand and why?",
        "Suggest some budget-friendly accommodations in Bali.",
        "What cultural considerations should I be aware of when visiting Morocco?"
    ]
    
    results = {}
    
    print("\n===== TESTING PUBLIC API (OpenAI) =====\n")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest Prompt {i}: {prompt}")
        response = query_openai_api(prompt)
        print(f"\nOpenAI Response:\n{response}\n")
        print("-" * 80)
        
        # Store result
        if i not in results:
            results[i] = {}
        results[i]["OpenAI"] = response
    
    print("\n\n===== TESTING LOCAL LLAMA 3.2 =====\n")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest Prompt {i}: {prompt}")
        response = query_local_llama(prompt)
        print(f"\nLlama 3.2 Response:\n{response}\n")
        print("-" * 80)
        
        # Store result
        if i not in results:
            results[i] = {}
        results[i]["Llama 3.2"] = response
    
    return results

# Run tests if this file is executed directly
if __name__ == "__main__":
    results = test_travel_prompts()
    
    # Test a specific travel planning prompt
    comparison_prompt = """
    I'm planning a 7-day trip to Italy in June with my family (2 adults, 2 children ages 10 and 14).
    We're interested in historical sites, good food, and some outdoor activities.
    Our budget is around $5000 excluding flights.
    Can you suggest an itinerary that includes Rome and Florence?
    """
    
    print("\n===== MODEL COMPARISON =====\n")
    print(f"Prompt: {comparison_prompt}\n")
    
    responses = compare_models(comparison_prompt)
    
    print("OpenAI Response:")
    print(responses["OpenAI"])
    print("\n" + "-" * 80 + "\n")
    
    print("Llama 3.2 Response:")
    print(responses["Llama 3.2"])