#!/usr/bin/env python3
"""
Test script for document upload and extraction.
"""
import requests
import time
import sys

# Configuration
API_URL = "http://localhost:8000"
TEST_FILE = "test_document.txt"  # Change to your test file path
ACCESS_TOKEN = None  # Set your access token here if testing with auth

def create_test_file():
    """Create a simple test document."""
    content = """
# Financial Summary 2024

## Income
- Salary: $75,000
- Bonus: $5,000
- Investment Income: $2,500

## Expenses
- Rent: $24,000
- Utilities: $3,600
- Food: $6,000
- Transportation: $4,800

## Savings
- Emergency Fund: $15,000
- Retirement (401k): $45,000
- Investment Portfolio: $30,000

## Goals
- Increase emergency fund to $20,000 by end of year
- Max out 401k contributions
- Start saving for house down payment
"""
    with open(TEST_FILE, 'w') as f:
        f.write(content)
    print(f"✓ Created test file: {TEST_FILE}")

def upload_file():
    """Upload file to the API."""
    print(f"\n📤 Uploading {TEST_FILE}...")
    
    headers = {}
    if ACCESS_TOKEN:
        headers['Authorization'] = f'Bearer {ACCESS_TOKEN}'
    
    with open(TEST_FILE, 'rb') as f:
        files = {'files': (TEST_FILE, f, 'text/plain')}
        response = requests.post(
            f"{API_URL}/api/upload",
            files=files,
            headers=headers
        )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Upload successful!")
        print(f"  - Total files: {result['total']}")
        print(f"  - Successful: {result['successCount']}")
        print(f"  - Failed: {result['failedCount']}")
        
        if result['successful']:
            doc = result['successful'][0]
            print(f"\n📄 Document Info:")
            print(f"  - File: {doc['fileName']}")
            print(f"  - URL: {doc['fileUrl']}")
            print(f"  - Document ID: {doc['documentId']}")
            print(f"  - Status: {doc['extractionStatus']}")
            return doc['documentId']
    else:
        print(f"✗ Upload failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def check_status(document_id, max_attempts=30):
    """Check extraction status."""
    print(f"\n⏳ Checking extraction status (Document ID: {document_id})...")
    
    for attempt in range(max_attempts):
        try:
            # Query Supabase directly or add a status endpoint
            print(f"  Attempt {attempt + 1}/{max_attempts}...", end='\r')
            time.sleep(2)
            
            # You can check the database directly or add this endpoint:
            # response = requests.get(f"{API_URL}/api/documents/{document_id}/status")
            
        except Exception as e:
            print(f"\n  Error checking status: {e}")
    
    print("\n⚠️  Check your Supabase database to see the extraction results:")
    print(f"     SELECT * FROM user_uploaded_documents WHERE id = {document_id};")

def main():
    """Run the test."""
    print("=" * 60)
    print("Document Upload & Extraction Test")
    print("=" * 60)
    
    # Create test file
    create_test_file()
    
    # Upload file
    document_id = upload_file()
    
    if document_id:
        print("\n✓ File uploaded successfully!")
        print("  Background extraction and summarization is running...")
        print("\n📊 To check results, run this SQL in Supabase:")
        print(f"     SELECT id, \"fileName\", \"extractionStatus\", ")
        print(f"            LENGTH(\"extractedContent\") as content_length,")
        print(f"            LENGTH(summary) as summary_length")
        print(f"     FROM user_uploaded_documents")
        print(f"     WHERE id = {document_id};")
        print("\n  Or wait 10-30 seconds and check the full summary:")
        print(f"     SELECT summary FROM user_uploaded_documents WHERE id = {document_id};")
    else:
        print("\n✗ Upload failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
