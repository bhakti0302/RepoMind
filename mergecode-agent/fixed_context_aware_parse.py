def _context_aware_parse(self, instruction_block: str) -> List[Dict[str, Any]]:
    """
    Parse an instruction block with context awareness.
    
    Args:
        instruction_block: The instruction block to parse
        
    Returns:
        A list of actions
    """
    # Split the instruction into steps or sections
    sections = re.split(r"##\s+Step \d+:|##\s+[\w\s]+:", instruction_block)
    sections = [s.strip() for s in sections if s.strip()]
    
    # If there are no clear sections, return empty list to fall back to LLM parsing
    if len(sections) <= 1:
        return []
    
    # Initialize context
    context = {
        "current_file_path": None,
        "code_blocks": []
    }
    
    # Extract code blocks
    code_block_pattern = r"```(?:\w+)?\n(.*?)```"
    for match in re.finditer(code_block_pattern, instruction_block, re.DOTALL):
        context["code_blocks"].append(match.group(1))
    
    # Look for file paths with backticks
    backtick_path_match = re.search(r"`([^`]+)`", instruction_block)
    if backtick_path_match:
        context["current_file_path"] = backtick_path_match.group(1)
        print(f"Found file path in backticks: {context['current_file_path']}")
    
    # Process each section with context
    actions = []
    
    for section in sections:
        # Look for file paths in this section
        file_path_match = re.search(r"(?:Create|Add|Modify).*?['\"]?([\w\/\.\-]+)['\"]?", section, re.IGNORECASE)
        if file_path_match:
            context["current_file_path"] = file_path_match.group(1)
            print(f"Found file path in section: {context['current_file_path']}")
        
        # Also look for paths in backticks in this section
        backtick_path_match = re.search(r"`([^`]+)`", section)
        if backtick_path_match:
            context["current_file_path"] = backtick_path_match.group(1)
            print(f"Found file path in backticks in section: {context['current_file_path']}")
        
        # Check if this section is about creating a file
        if re.search(r"Create a (?:new )?file", section, re.IGNORECASE) and context["current_file_path"]:
            # Look for a code block in this section or in the next section
            code_block = None
            if context["code_blocks"]:
                code_block = context["code_blocks"][0]  # Just peek, don't pop yet
            
            actions.append({
                "action": "create_file",
                "file_path": context["current_file_path"],
                "content": code_block or ""
            })
            
            # Now pop the code block if we used it
            if code_block and context["code_blocks"]:
                context["code_blocks"].pop(0)
        
        # Check if this section is about adding code to a file
        elif re.search(r"Add (?:the )?(?:generated )?code", section, re.IGNORECASE) and context["current_file_path"]:
            # Look for a code block in this section or in the next section
            code_block = None
            if context["code_blocks"]:
                code_block = context["code_blocks"][0]  # Just peek, don't pop yet
            
            if code_block:
                actions.append({
                    "action": "modify_file",
                    "file_path": context["current_file_path"],
                    "instruction": f"Add the following code to the file:\n\n{code_block}"
                })
                
                # Now pop the code block if we used it
                if context["code_blocks"]:
                    context["code_blocks"].pop(0)
    
    # If we have actions from context-aware parsing, return them
    if actions:
        print("Using context-aware parsing")
        return actions
    
    # Otherwise, return empty list to fall back to LLM parsing
    return []
