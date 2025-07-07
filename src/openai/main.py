#!/usr/bin/env python
import sys
import warnings

from datetime import datetime
from crew import researcher
from tools.detect_language import detect_language

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    user_input = "Saya Merasa Stress dan cemas"
    language = detect_language(user_input)
    
    inputs = {
        'keluhan_user': user_input,
        'language' : language
    }
    
    print("Language detected:", language)
    print("Context:", inputs)
    
    try:
        researcher().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

run()


