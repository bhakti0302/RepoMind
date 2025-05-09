"""
Script to inspect module contents for debugging import issues.
"""
import importlib
import inspect
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def inspect_module(module_name):
    """Inspect a module and print its contents."""
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        print(f"\n=== Module: {module_name} ===")
        
        # Get all attributes
        attributes = dir(module)
        
        # Filter out built-in attributes
        public_attrs = [attr for attr in attributes if not attr.startswith('__')]
        
        # Print functions
        functions = [attr for attr in public_attrs if inspect.isfunction(getattr(module, attr))]
        if functions:
            print("\nFunctions:")
            for func in functions:
                print(f"  - {func}")
        
        # Print classes
        classes = [attr for attr in public_attrs if inspect.isclass(getattr(module, attr))]
        if classes:
            print("\nClasses:")
            for cls in classes:
                print(f"  - {cls}")
        
        # Print variables
        variables = [attr for attr in public_attrs if not inspect.isfunction(getattr(module, attr)) and not inspect.isclass(getattr(module, attr))]
        if variables:
            print("\nVariables:")
            for var in variables:
                print(f"  - {var}")
        
        return True
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")
        return False
    except Exception as e:
        print(f"Error inspecting {module_name}: {e}")
        return False

if __name__ == "__main__":
    # List of modules to inspect
    modules = [
        "codebase_analyser.embeddings.embedding_generator",
        "codebase_analyser.database.lancedb_manager",
        "codebase_analyser.database.unified_storage"
    ]
    
    for module in modules:
        inspect_module(module)