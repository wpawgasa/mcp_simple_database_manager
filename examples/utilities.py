from mcp.types import CallToolResult, TextContent


def extract_text_content(result: CallToolResult) -> str:
    """Safely extract text content from MCP result."""
    if result.content and isinstance(result.content[0], TextContent):
        return result.content[0].text
    return "No text content available"
