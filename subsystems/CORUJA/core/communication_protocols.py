# CORUJA Core - Communication Protocols

"""Placeholder for defining standard communication protocols for AI interactions."""

# Example structure
STANDARD_PROMPTS = {
    "summarize": "Provide a concise summary of the following text: {text}",
    "analyze_sentiment": "Analyze the sentiment (positive, negative, neutral) "
    "of this message: {message}",
}


def format_prompt(protocol_name: str, **kwargs) -> str:
    """Formats a standard prompt with given arguments."""
    if protocol_name in STANDARD_PROMPTS:
        try:
            return STANDARD_PROMPTS[protocol_name].format(**kwargs)
        except KeyError as e:
            # Handle missing arguments
            print(f"Error formatting prompt '{protocol_name}': Missing argument {e}")
            return None
    else:
        print(f"Error: Unknown protocol '{protocol_name}'")
        return None
