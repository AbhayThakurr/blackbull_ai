import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.graph.builder import graph

def test_yami():
    input_state = {"user_input": "Hey Yami, what should we do today?"}
    result = graph.invoke(input_state)
    print(f"User: {input_state['user_input']}")
    print(f"Yami: {result['response']}")

if __name__ == "__main__":
    try:
        test_yami()
    except Exception as e:
        print(f"Error: {e}")
