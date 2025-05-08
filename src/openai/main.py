#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crew import researcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    inputs = {
        'keluhan_user': 'saya demam, batuk, dan pilek',
    }

    try:
        researcher().run(inputs)  # Ganti dari .crew().kickoff() ke .run()
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

run()

