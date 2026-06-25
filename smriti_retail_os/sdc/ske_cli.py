# -*- coding: utf-8 -*-
#
# @file: sdc/ske_cli.py
# @description: Command-Line Interface for SMRITI Knowledge Engine (SKE)
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.1.2-GA
#

import sys
import os

# Add sdc folder to import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ske import SMRITIKnowledgeEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python sdc/ske_cli.py \"<query_text>\" [--format markdown|json|text]")
        sys.exit(1)

    query = sys.argv[1]
    
    # Parse format argument
    output_format = "markdown"
    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        engine = SMRITIKnowledgeEngine(repo_root)
        response = engine.resolve(query, output_format=output_format)
        print(response)
    except Exception as e:
        print(f"SKE Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
