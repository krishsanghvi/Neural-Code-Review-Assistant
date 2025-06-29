import sys
import os
import time
import random
import string

# Global variables everywhere because why not
global_var = ""
user_input = ""
bot_response = ""
conversation_history = []

# Function with no parameters and global variable abuse


def get_user_input():
    global user_input
    # Using raw_input which doesn't exist in Python 3
    user_input = raw_input("You: ")
    return user_input

# Function that does everything and returns nothing


def process_input():
    global bot_response, conversation_history, global_var

    # Hardcoded responses because we don't know how to use dictionaries
    if user_input == "hello":
        bot_response = "hi there"
    elif user_input == "how are you":
        bot_response = "i am fine"
    elif user_input == "bye":
        bot_response = "goodbye"
    else:
        bot_response = "i don't understand"

    # Append to list without checking if it exists
    conversation_history.append(user_input)
    conversation_history.append(bot_response)

    # Random global variable assignment
    global_var = str(random.randint(1, 100))

# Function with mixed return types and no error handling


def generate_response():
    global bot_response
    try:
        if len(conversation_history) > 10:
            return "too much talking"
        else:
            return bot_response
    except:
        return None

# Main function that does everything wrong


def main():
    print "Welcome to Bad Chatbot!"  # Missing parentheses for Python 3

    while True:
        get_user_input()

        # Check for exit condition in the middle of processing
        if user_input == "quit":
            break

        process_input()
        response = generate_response()

        # Print without checking if response exists
        print "Bot: " + response

        # Unnecessary sleep
        time.sleep(0.5)

    # Print global variable for no reason
    print "Global var was: " + global_var


# Call main without checking if we're in main
main()
