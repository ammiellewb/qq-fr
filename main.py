#!/usr/bin/env python3

"""
Main entry point for the translation pipeline.
This script runs the complete ETL process: Extract strings from code files,
Filter them to keep only user-facing text, Translate them, and save the results.
"""

import argparse
import sys
import os

from config import (
    OPENAI_API_KEY, DEEPL_API_KEY, 
    DEFAULT_DIRECTORY, DEFAULT_TARGET_LANGUAGE, 
    DEFAULT_FILE_EXTENSIONS
)
from translation_pipeline import TranslationPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Extract, filter, and translate user-facing strings from code files."
    )
    
    parser.add_argument(
        '-d', '--directory', 
        type=str, 
        default=DEFAULT_DIRECTORY,
        help=f'Directory to scan for code files (default: {DEFAULT_DIRECTORY})'
    )
    
    parser.add_argument(
        '--openai-key', 
        type=str, 
        default=OPENAI_API_KEY,
        help='OpenAI API key (can also be set as OPENAI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--deepl-key', 
        type=str, 
        default=DEEPL_API_KEY,
        help='DeepL API key (can also be set as DEEPL_API_KEY env var)'
    )
    
    parser.add_argument(
        '-l', '--target-lang', 
        type=str, 
        default=DEFAULT_TARGET_LANGUAGE,
        help=f'Target language code (default: {DEFAULT_TARGET_LANGUAGE})'
    )
    
    parser.add_argument(
        '--save-intermediates', 
        action='store_true', 
        help='Save intermediate results to files'
    )
    
    parser.add_argument(
        '-e', '--extensions', 
        type=str, 
        nargs='+', 
        default=DEFAULT_FILE_EXTENSIONS,
        help='List of file extensions to scan (default: .js .jsx .ts .tsx .html .vue .py)'
    )
    
    args = parser.parse_args()
    
    # Validate required API keys
    if not args.openai_key:
        print("ERROR: OpenAI API key is required. Set it using --openai-key or OPENAI_API_KEY env var")
        sys.exit(1)
        
    if not args.deepl_key:
        print("ERROR: DeepL API key is required. Set it using --deepl-key or DEEPL_API_KEY env var")
        sys.exit(1)
    
    # Validate directory exists
    if not os.path.isdir(args.directory):
        print(f"ERROR: Directory not found: {args.directory}")
        sys.exit(1)
    
    # Create and run the pipeline
    pipeline = TranslationPipeline(
        openai_api_key=args.openai_key,
        deepl_api_key=args.deepl_key,
        file_extensions=args.extensions
    )
    
    pipeline.run(
        directory=args.directory,
        target_lang=args.target_lang,
        save_intermediates=args.save_intermediates
    )


if __name__ == "__main__":
    main()