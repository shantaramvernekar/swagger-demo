from typing import Optional, List, Dict, Any
import requests
from langchain.tools import StructuredTool


def create_api_tools(api_base_url: str, api_key: Optional[str] = None) -> List[StructuredTool]:
    """
    Create tools for interacting with the REST API.
    """
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    def health_check() -> str:
        """Check the health status of the API."""
        try:
            response = requests.get(f"{api_base_url}/health")
            response.raise_for_status()
            return f"API is healthy: {response.json()}"
        except Exception as e:
            return f"Error checking health: {str(e)}"
    
    def create_item(name: str, price: float, tags: Optional[List[str]] = None) -> str:
        """Create a new item. Args: name (str), price (float), tags (optional list of strings)."""
        try:
            payload = {"name": name, "price": price}
            if tags:
                payload["tags"] = tags
            response = requests.post(
                f"{api_base_url}/items",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            item = response.json()
            return f"Created item: {item}"
        except Exception as e:
            return f"Error creating item: {str(e)}"
    
    def list_items(query: Optional[str] = None, limit: int = 10) -> str:
        """List items. Args: query (optional search string), limit (max items to return, default 10)."""
        try:
            params = {"limit": limit}
            if query:
                params["q"] = query
            response = requests.get(
                f"{api_base_url}/items",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            items = response.json()
            return f"Found {len(items)} items: {items}"
        except Exception as e:
            return f"Error listing items: {str(e)}"
    
    def get_item(item_id: int) -> str:
        """Get a specific item by ID. Args: item_id (integer)."""
        try:
            response = requests.get(
                f"{api_base_url}/items/{item_id}",
                headers=headers
            )
            response.raise_for_status()
            return f"Item details: {response.json()}"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return f"Item with ID {item_id} not found"
            return f"Error getting item: {str(e)}"
        except Exception as e:
            return f"Error getting item: {str(e)}"
    
    def update_item(item_id: int, name: str, price: float, tags: Optional[List[str]] = None) -> str:
        """Update an existing item. Args: item_id (int), name (str), price (float), tags (optional list)."""
        try:
            payload = {"name": name, "price": price}
            if tags:
                payload["tags"] = tags
            response = requests.put(
                f"{api_base_url}/items/{item_id}",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            item = response.json()
            return f"Updated item: {item}"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return f"Item with ID {item_id} not found"
            return f"Error updating item: {str(e)}"
        except Exception as e:
            return f"Error updating item: {str(e)}"
    
    def delete_item(item_id: int) -> str:
        """Delete an item by ID. Args: item_id (integer)."""
        try:
            response = requests.delete(
                f"{api_base_url}/items/{item_id}",
                headers=headers
            )
            if response.status_code == 204:
                return f"Successfully deleted item {item_id}"
            response.raise_for_status()
            return f"Deleted item: {response.json()}"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return f"Item with ID {item_id} not found"
            return f"Error deleting item: {str(e)}"
        except Exception as e:
            return f"Error deleting item: {str(e)}"
    
    def upload_file(file_path: str) -> str:
        """Upload a file. Args: file_path (path to the file to upload)."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{api_base_url}/files/upload",
                    files=files,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                return f"File uploaded successfully: {result}"
        except FileNotFoundError:
            return f"Error: File not found at {file_path}"
        except Exception as e:
            return f"Error uploading file: {str(e)}"
    
    def get_secret() -> str:
        """Get secret from secure endpoint (requires API key)."""
        if not api_key:
            return "Error: API key required for secure endpoint"
        try:
            response = requests.get(
                f"{api_base_url}/secure/secret",
                headers=headers
            )
            response.raise_for_status()
            return f"Secret: {response.json()}"
        except Exception as e:
            return f"Error accessing secret: {str(e)}"
    
    # Create Tool objects
    tools = [
        StructuredTool.from_function(
            name="health_check",
            func=health_check,
            description="Check if the API is healthy and running"
        ),
        StructuredTool.from_function(
            name="create_item",
            func=create_item,
            description="Create a new item with name, price, and optional tags"
        ),
        StructuredTool.from_function(
            name="list_items",
            func=list_items,
            description="List all items, optionally filtered by search query"
        ),
        StructuredTool.from_function(
            name="get_item",
            func=get_item,
            description="Get details of a specific item by its ID"
        ),
        StructuredTool.from_function(
            name="update_item",
            func=update_item,
            description="Update an existing item's name, price, and tags"
        ),
        StructuredTool.from_function(
            name="delete_item",
            func=delete_item,
            description="Delete an item by its ID"
        ),
        StructuredTool.from_function(
            name="upload_file",
            func=upload_file,
            description="Upload a file to the server"
        ),
        StructuredTool.from_function(
            name="get_secret",
            func=get_secret,
            description="Get secret from secure endpoint (requires API key)"
        ),
    ]
    
    return tools

