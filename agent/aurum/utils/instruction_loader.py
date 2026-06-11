import os 

def load_instruction_from_file( filename : str, default_instuction: str = "You are a helper agent for financial services") -> str:
    """
    Reads instruction text from a file relative to agent instruction.
    input para :
        - filename str
        - default_instruction str

    returns: instruction str
"""
    instruction = default_instuction 
    try:
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        with open(filepath, "r", encoding="utf-8") as f:
            insuction = f.read()
        print(f"Successfully loaded instruction from {filename}")
    
    except FileNotFoundError:
        print(f"WARNING: Instruction file not found:{filepath}. Using default.")
    except Exception as e:
        print(f"ERROR loading instruction file {filepath}: {e}. Using default.")
    return instruction


