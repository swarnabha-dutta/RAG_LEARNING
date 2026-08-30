from candidate import load_candidate
from prompts import build_system_prompt
from llm import ask_llm


# 1. Load candidate information
candidate = load_candidate()

# 2. Build the system prompt
system_prompt = build_system_prompt(candidate)

# 3. Conversation history
messages = [
    {
        "role":"system",
        "content":system_prompt
    }
]



def chat(question: str):
    # Add user's question
    messages.append({
        "role":"user",
        "content":question
    })

    # Send conversation  to LLM 
    answer = ask_llm(messages)

    # Save AI's answer as assistant message
    messages.append({
        "role":"assistant",
        "content":answer
    })

    return answer


# Test The Conversation

if __name__ == "__main__":
    print("AI Candidate Chat")
    print("Type 'exit' to quit.\n")


    while True:

        question = input("You: ")

        if question.lower() in ["exit", "exit()", "quit", "quit()"]:
            print("Goodbye!")
            break

        if not question.strip():
            continue
        
        print("AI: ",end="")


        chat(question)
        
