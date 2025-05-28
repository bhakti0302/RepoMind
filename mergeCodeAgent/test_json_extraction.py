#!/usr/bin/env python3
import sys
import json
import re

# Add the path to the mergeCodeAgent directory
sys.path.append('.')

def extract_json_from_response(response):
    """
    Extract JSON from a response that might be wrapped in code fences.
    
    Args:
        response: The response string from the LLM
        
    Returns:
        Parsed JSON data
    
    Raises:
        ValueError: If JSON cannot be parsed
    """
    if not response or response.strip() == "":
        raise ValueError("Empty response from LLM")
        
    print(f"Extracting JSON from response (length: {len(response)}, first 100 chars: {response[:100]}...)")
    
    # Try to parse as direct JSON first
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Direct JSON parsing failed: {e}")
        
        # Response might be wrapped in markdown code fences
        # Look for patterns like ```json ... ``` or just ``` ... ```
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, response)
        
        if matches:
            print(f"Found {len(matches)} potential JSON blocks in code fences")
            for i, potential_json in enumerate(matches):
                print(f"Trying potential JSON block {i+1} (length: {len(potential_json)})")
                try:
                    return json.loads(potential_json)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse block {i+1}: {e}")
                    # Try cleaning the JSON a bit
                    try:
                        # Remove common issues
                        cleaned = potential_json.strip()
                        cleaned = re.sub(r'\\([^"])', r'\1', cleaned)  # Fix unnecessary escapes
                        cleaned = re.sub(r'\\\\([^"])', r'\\\1', cleaned)  # Keep legitimate escapes
                        if cleaned != potential_json:
                            print(f"Cleaned JSON block, trying again...")
                            return json.loads(cleaned)
                    except json.JSONDecodeError:
                        print("Cleaning did not help, continuing to next block")
                        continue
        
        # Try to find any JSON-like structure in the response
        # This is a more aggressive approach
        print("Looking for any JSON-like structure in the response...")
        try:
            # First try to find a complete JSON object
            pattern = r'({[\s\S]*})'
            match = re.search(pattern, response)
            if match:
                potential_json = match.group(1)
                print(f"Found potential JSON object (length: {len(potential_json)})")
                try:
                    return json.loads(potential_json)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON object: {e}")
                    # Try cleaning the JSON
                    try:
                        # Remove common issues
                        cleaned = potential_json.strip()
                        cleaned = re.sub(r'\\([^"])', r'\1', cleaned)  # Fix unnecessary escapes
                        cleaned = re.sub(r'\\\\([^"])', r'\\\1', cleaned)  # Keep legitimate escapes
                        if cleaned != potential_json:
                            print(f"Cleaned JSON object, trying again...")
                            return json.loads(cleaned)
                    except json.JSONDecodeError:
                        print("Cleaning did not help")
            
            # Try an even more aggressive approach - construct a minimal valid JSON
            print("Attempting to construct a valid JSON from the response...")
            # Look for modification_type
            mod_type_match = re.search(r'"modification_type"\s*:\s*"([^"]*)"', response)
            if mod_type_match:
                mod_type = mod_type_match.group(1)
                print(f"Found modification_type: {mod_type}")
                
                # Look for new_content with better multiline handling
                # This pattern handles both escaped sequences and raw multiline content
                try:
                    # First try standard format with escaped content
                    content_match = re.search(r'"new_content"\s*:\s*"((?:\\.|[^"])*)"', response)
                    if content_match:
                        new_content = content_match.group(1)
                        print(f"Found new_content (length: {len(new_content)})")
                    else:
                        # Try to handle raw multiline content between quotes
                        content_start_match = re.search(r'"new_content"\s*:\s*"', response)
                        if content_start_match:
                            start_pos = content_start_match.end()
                            # Find the end quote that's not escaped
                            content_end_match = None
                            for match in re.finditer(r'(?<!\\)"', response[start_pos:]):
                                content_end_match = match
                                break
                            
                            if content_end_match:
                                end_pos = start_pos + content_end_match.start()
                                new_content = response[start_pos:end_pos]
                                print(f"Extracted multiline content (length: {len(new_content)})")
                            else:
                                # If no end quote, try to extract until the end of the string or a closing brace
                                brace_match = re.search(r'}', response[start_pos:])
                                if brace_match:
                                    end_pos = start_pos + brace_match.start()
                                    new_content = response[start_pos:end_pos].strip()
                                    print(f"Extracted content until closing brace (length: {len(new_content)})")
                                else:
                                    new_content = response[start_pos:].strip()
                                    print(f"Extracted remaining content (length: {len(new_content)})")
                        else:
                            # Try to extract any content between the modification_type and the end
                            content_extract = response.split('"modification_type"')[1]
                            if "new_content" in content_extract:
                                content_extract = content_extract.split("new_content")[1].strip()
                                if content_extract.startswith(":"):
                                    content_extract = content_extract[1:].strip()
                                if content_extract.startswith('"'):
                                    content_extract = content_extract[1:].strip()
                                # Get content until the next closing quote or the end
                                end_match = re.search(r'(?<!\\)"', content_extract)
                                if end_match:
                                    new_content = content_extract[:end_match.start()]
                                else:
                                    new_content = content_extract
                                
                                print(f"Extracted content using split (length: {len(new_content)})")
                            else:
                                raise ValueError("Could not locate new_content")
                    
                    # Construct a minimal valid JSON
                    reconstructed_json = {
                        "modification_type": mod_type,
                        "new_content": new_content
                    }
                    print("Successfully reconstructed JSON from fragments")
                    return reconstructed_json
                except Exception as e:
                    print(f"Error extracting new_content: {e}")
        except Exception as e:
            print(f"Error in aggressive JSON extraction: {e}")
            
        # If we get here, we couldn't parse JSON
        raise ValueError(f"Could not parse LLM response as JSON")

def main():
    # Test case 1: JSON wrapped in code fences
    test_case_1 = '''```json
{
  "modification_type": "replace_file",
  "new_content": "entity Incidents {\\n  key ID : UUID;\\n  createdAt : Timestamp;\\n  createdBy : String;\\n  modifiedAt : Timestamp;\\n  modifiedBy : String;\\n  title : String;\\n  description : String;\\n  status : Association to Status;\\n  priority : Association to Priority default 'M';\\n  urgency : Association to Urgency;\\n  impact : Association to Impact;\\n  customer : Association to Customers;\\n  assignedTo : Association to Employees;\\n}"
}
```'''

    # Test case 2: Plain JSON
    test_case_2 = '''{
  "modification_type": "replace_file",
  "new_content": "entity Incidents {\\n  key ID : UUID;\\n  createdAt : Timestamp;}"
}'''

    # Test case 3: JSON embedded in other text
    test_case_3 = '''Here's the JSON you requested:
```
{
  "modification_type": "replace_file",
  "new_content": "entity Incidents {\\n  key ID : UUID;}"
}
```
Let me know if you need anything else.'''

    # Test case 4: Broken JSON with unnecessary escapes
    test_case_4 = '''```json
{
  \"modification_type\": \"replace_file\",
  \"new_content\": \"entity Incidents {\\n  key ID : UUID;\\n}\"
}
```'''

    # Test case 5: Malformed JSON that requires regex extraction
    test_case_5 = '''I'll provide the modification details for your file:

The modification type is "replace_file" and the new content should be:

"modification_type": "replace_file",
"new_content": "entity Incidents {\\n  key ID : UUID;\\n  description : String;\\n}"
'''

    # Test case 6: JSON with broken quotes that needs aggressive reconstruction
    test_case_6 = '''The JSON is as follows:
{
  "modification_type": "replace_file",
  "new_content": "entity Incidents {\n  key ID : UUID;\n  createdAt : Timestamp;\n}
}'''

    print("=== Testing JSON extraction with different formats ===")
    
    try:
        print("\n=== Test Case 1: JSON wrapped in code fences ===")
        result_1 = extract_json_from_response(test_case_1)
        print(f"Result: {json.dumps(result_1, indent=2)[:100]}...")
        
        print("\n=== Test Case 2: Plain JSON ===")
        result_2 = extract_json_from_response(test_case_2)
        print(f"Result: {json.dumps(result_2, indent=2)[:100]}...")
        
        print("\n=== Test Case 3: JSON embedded in other text ===")
        result_3 = extract_json_from_response(test_case_3)
        print(f"Result: {json.dumps(result_3, indent=2)[:100]}...")
        
        print("\n=== Test Case 4: Broken JSON with unnecessary escapes ===")
        result_4 = extract_json_from_response(test_case_4)
        print(f"Result: {json.dumps(result_4, indent=2)[:100]}...")
        
        print("\n=== Test Case 5: Malformed JSON requiring regex extraction ===")
        result_5 = extract_json_from_response(test_case_5)
        print(f"Result: {json.dumps(result_5, indent=2)[:100]}...")
        
        print("\n=== Test Case 6: JSON with broken quotes needing reconstruction ===")
        result_6 = extract_json_from_response(test_case_6)
        print(f"Result: {json.dumps(result_6, indent=2)[:100]}...")
        
        print("\nAll test cases passed!")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 