#!/usr/bin/env python3

import asyncio
import json
import os
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

class ITGlueServer:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv('ITGLUE_API_KEY')
        self.base_url = os.getenv('ITGLUE_BASE_URL', 'https://api.itglue.com')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.server_name = os.getenv('SERVER_NAME', 'mcp-itglue-server')
        
        # Configure logging
        log_level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("ITGLUE_API_KEY environment variable is required")
            
        self.server = Server(self.server_name)
        self.setup_handlers()
        
        # Test connection on startup
        self._test_connection()

    def _test_connection(self):
        """Test IT Glue API connection and authentication"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.base_url}/organizations", headers=headers, timeout=10)
            if response.status_code == 401:
                raise ValueError("Invalid IT Glue API key")
            elif response.status_code != 200:
                raise ValueError(f"IT Glue API connection failed: {response.status_code}")
            self.logger.info("Successfully connected to IT Glue API")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to IT Glue: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for IT Glue API requests"""
        return {
            'Content-Type': 'application/vnd.api+json',
            'x-api-key': self.api_key,
            'User-Agent': f'{self.server_name}/1.0'
        }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to IT Glue API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, params=params, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    raise Exception(f"IT Glue API Error: {error_detail}")
                except:
                    raise Exception(f"IT Glue API Error: HTTP {e.response.status_code}")
            raise Exception(f"IT Glue API Request Failed: {str(e)}")

    def setup_handlers(self):
        """Setup MCP tool handlers"""
        
        # Organization Management Tools
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="list_organizations",
                    description="List all organizations in IT Glue with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Filter by organization name"},
                                    "organization_type_id": {"type": "integer", "description": "Filter by organization type ID"},
                                    "organization_status_id": {"type": "integer", "description": "Filter by organization status ID"}
                                },
                                "description": "Optional filters to apply to the organization list"
                            },
                            "sort": {
                                "type": "string", 
                                "description": "Sort field (e.g., 'name', 'created_at', 'updated_at')",
                                "default": "name"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Number of results per page (1-1000)",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 1000
                            },
                            "page_number": {
                                "type": "integer",
                                "description": "Page number to retrieve",
                                "default": 1,
                                "minimum": 1
                            }
                        }
                    }
                ),
                Tool(
                    name="get_organization",
                    description="Get specific organization details by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "IT Glue organization ID"
                            }
                        },
                        "required": ["organization_id"]
                    }
                ),
                Tool(
                    name="create_organization",
                    description="Create a new organization in IT Glue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Organization name"
                            },
                            "organization_type_id": {
                                "type": "integer",
                                "description": "Organization type ID"
                            },
                            "organization_status_id": {
                                "type": "integer",
                                "description": "Organization status ID"
                            },
                            "description": {
                                "type": "string",
                                "description": "Organization description"
                            },
                            "alert": {
                                "type": "string",
                                "description": "Alert message for the organization"
                            }
                        },
                        "required": ["name", "organization_type_id"]
                    }
                ),
                Tool(
                    name="update_organization",
                    description="Update an existing organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "IT Glue organization ID"
                            },
                            "name": {
                                "type": "string",
                                "description": "Organization name"
                            },
                            "organization_type_id": {
                                "type": "integer",
                                "description": "Organization type ID"
                            },
                            "organization_status_id": {
                                "type": "integer",
                                "description": "Organization status ID"
                            },
                            "description": {
                                "type": "string",
                                "description": "Organization description"
                            },
                            "alert": {
                                "type": "string",
                                "description": "Alert message for the organization"
                            }
                        },
                        "required": ["organization_id"]
                    }
                ),
                Tool(
                    name="list_configurations",
                    description="Get all configurations with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "Filter by organization ID"
                            },
                            "filter": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Filter by configuration name"},
                                    "configuration_type_id": {"type": "integer", "description": "Filter by configuration type ID"},
                                    "configuration_status_id": {"type": "integer", "description": "Filter by configuration status ID"},
                                    "contact_id": {"type": "integer", "description": "Filter by contact ID"},
                                    "serial_number": {"type": "string", "description": "Filter by serial number"}
                                },
                                "description": "Optional filters to apply"
                            },
                            "sort": {
                                "type": "string",
                                "description": "Sort field",
                                "default": "name"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Number of results per page (1-1000)",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 1000
                            },
                            "page_number": {
                                "type": "integer",
                                "description": "Page number to retrieve",
                                "default": 1,
                                "minimum": 1
                            }
                        }
                    }
                ),
                Tool(
                    name="get_configuration",
                    description="Get specific configuration details by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "configuration_id": {
                                "type": "integer",
                                "description": "IT Glue configuration ID"
                            }
                        },
                        "required": ["configuration_id"]
                    }
                ),
                Tool(
                    name="create_configuration",
                    description="Create a new configuration item",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "Organization ID"
                            },
                            "name": {
                                "type": "string",
                                "description": "Configuration name"
                            },
                            "configuration_type_id": {
                                "type": "integer",
                                "description": "Configuration type ID"
                            },
                            "configuration_status_id": {
                                "type": "integer",
                                "description": "Configuration status ID"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Configuration notes"
                            },
                            "serial_number": {
                                "type": "string",
                                "description": "Serial number"
                            },
                            "asset_tag": {
                                "type": "string",
                                "description": "Asset tag"
                            }
                        },
                        "required": ["organization_id", "name", "configuration_type_id"]
                    }
                ),
                Tool(
                    name="list_configuration_types",
                    description="Get all available configuration types",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_flexible_assets",
                    description="Get flexible assets with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "Filter by organization ID"
                            },
                            "flexible_asset_type_id": {
                                "type": "integer",
                                "description": "Filter by flexible asset type ID"
                            },
                            "filter": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Filter by asset name"}
                                },
                                "description": "Optional filters to apply"
                            },
                            "sort": {
                                "type": "string",
                                "description": "Sort field",
                                "default": "name"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Number of results per page (1-1000)",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        }
                    }
                ),
                Tool(
                    name="get_flexible_asset",
                    description="Get specific flexible asset details by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "flexible_asset_id": {
                                "type": "integer",
                                "description": "IT Glue flexible asset ID"
                            }
                        },
                        "required": ["flexible_asset_id"]
                    }
                ),
                Tool(
                    name="list_passwords",
                    description="Get passwords with optional filtering (secure)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "Filter by organization ID"
                            },
                            "filter": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Filter by password name"},
                                    "username": {"type": "string", "description": "Filter by username"},
                                    "url": {"type": "string", "description": "Filter by URL"}
                                },
                                "description": "Optional filters to apply"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Number of results per page (1-1000)",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        }
                    }
                ),
                Tool(
                    name="get_password",
                    description="Get specific password details by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "password_id": {
                                "type": "integer",
                                "description": "IT Glue password ID"
                            }
                        },
                        "required": ["password_id"]
                    }
                ),
                Tool(
                    name="list_documents",
                    description="Get documents with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "Filter by organization ID"
                            },
                            "filter": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Filter by document name"}
                                },
                                "description": "Optional filters to apply"
                            },
                            "sort": {
                                "type": "string",
                                "description": "Sort field",
                                "default": "name"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Number of results per page (1-1000)",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        }
                    }
                ),
                Tool(
                    name="get_document",
                    description="Get specific document details by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {
                                "type": "integer",
                                "description": "IT Glue document ID"
                            }
                        },
                        "required": ["document_id"]
                    }
                ),
                Tool(
                    name="list_contacts",
                    description="Get all contacts with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "Filter by organization ID"
                            },
                            "filter": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Filter by contact name"},
                                    "contact_type_id": {"type": "integer", "description": "Filter by contact type ID"}
                                },
                                "description": "Optional filters to apply"
                            },
                            "sort": {
                                "type": "string",
                                "description": "Sort field",
                                "default": "name"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Number of results per page (1-1000)",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        }
                    }
                ),
                Tool(
                    name="get_contact",
                    description="Get specific contact details by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contact_id": {
                                "type": "integer",
                                "description": "IT Glue contact ID"
                            }
                        },
                        "required": ["contact_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            try:
                if name == "list_organizations":
                    return await self._list_organizations(arguments)
                elif name == "get_organization":
                    return await self._get_organization(arguments)
                elif name == "create_organization":
                    return await self._create_organization(arguments)
                elif name == "update_organization":
                    return await self._update_organization(arguments)
                elif name == "list_configurations":
                    return await self._list_configurations(arguments)
                elif name == "get_configuration":
                    return await self._get_configuration(arguments)
                elif name == "create_configuration":
                    return await self._create_configuration(arguments)
                elif name == "list_configuration_types":
                    return await self._list_configuration_types(arguments)
                elif name == "list_flexible_assets":
                    return await self._list_flexible_assets(arguments)
                elif name == "get_flexible_asset":
                    return await self._get_flexible_asset(arguments)
                elif name == "list_passwords":
                    return await self._list_passwords(arguments)
                elif name == "get_password":
                    return await self._get_password(arguments)
                elif name == "list_documents":
                    return await self._list_documents(arguments)
                elif name == "get_document":
                    return await self._get_document(arguments)
                elif name == "list_contacts":
                    return await self._list_contacts(arguments)
                elif name == "get_contact":
                    return await self._get_contact(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                self.logger.error(f"Tool {name} failed: {str(e)}")
                return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

    # Organization Management Methods
    async def _list_organizations(self, args: dict):
        """List organizations with optional filtering"""
        params = {}
        
        if 'filter' in args and args['filter']:
            for key, value in args['filter'].items():
                params[f'filter[{key}]'] = value
                
        if 'sort' in args:
            params['sort'] = args['sort']
            
        params['page[size]'] = args.get('page_size', 50)
        params['page[number]'] = args.get('page_number', 1)
        
        data = self._make_request('GET', '/organizations', params=params)
        
        return [TextContent(
            type="text", 
            text=f"Found {len(data.get('data', []))} organizations:\n\n" + 
                 json.dumps(data, indent=2)
        )]

    async def _get_organization(self, args: dict):
        """Get specific organization by ID"""
        org_id = args['organization_id']
        data = self._make_request('GET', f'/organizations/{org_id}')
        
        return [TextContent(
            type="text",
            text=f"Organization {org_id} details:\n\n" + json.dumps(data, indent=2)
        )]

    async def _create_organization(self, args: dict):
        """Create new organization"""
        payload = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": args['name'],
                    "organization-type-id": args['organization_type_id']
                }
            }
        }
        
        # Add optional fields
        if 'organization_status_id' in args:
            payload["data"]["attributes"]["organization-status-id"] = args['organization_status_id']
        if 'description' in args:
            payload["data"]["attributes"]["description"] = args['description']
        if 'alert' in args:
            payload["data"]["attributes"]["alert"] = args['alert']
            
        data = self._make_request('POST', '/organizations', data=payload)
        
        return [TextContent(
            type="text",
            text=f"Successfully created organization:\n\n" + json.dumps(data, indent=2)
        )]

    async def _update_organization(self, args: dict):
        """Update existing organization"""
        org_id = args['organization_id']
        
        payload = {
            "data": {
                "type": "organizations",
                "attributes": {}
            }
        }
        
        # Add fields to update
        if 'name' in args:
            payload["data"]["attributes"]["name"] = args['name']
        if 'organization_type_id' in args:
            payload["data"]["attributes"]["organization-type-id"] = args['organization_type_id']
        if 'organization_status_id' in args:
            payload["data"]["attributes"]["organization-status-id"] = args['organization_status_id']
        if 'description' in args:
            payload["data"]["attributes"]["description"] = args['description']
        if 'alert' in args:
            payload["data"]["attributes"]["alert"] = args['alert']
            
        data = self._make_request('PATCH', f'/organizations/{org_id}', data=payload)
        
        return [TextContent(
            type="text",
            text=f"Successfully updated organization {org_id}:\n\n" + json.dumps(data, indent=2)
        )]

    # Configuration Management Methods
    async def _list_configurations(self, args: dict):
        """List configurations with optional filtering"""
        params = {}
        
        if 'organization_id' in args:
            params['filter[organization_id]'] = args['organization_id']
            
        if 'filter' in args and args['filter']:
            for key, value in args['filter'].items():
                params[f'filter[{key}]'] = value
                
        if 'sort' in args:
            params['sort'] = args['sort']
            
        params['page[size]'] = args.get('page_size', 50)
        params['page[number]'] = args.get('page_number', 1)
        
        data = self._make_request('GET', '/configurations', params=params)
        
        return [TextContent(
            type="text",
            text=f"Found {len(data.get('data', []))} configurations:\n\n" + 
                 json.dumps(data, indent=2)
        )]

    async def _get_configuration(self, args: dict):
        """Get specific configuration by ID"""
        config_id = args['configuration_id']
        data = self._make_request('GET', f'/configurations/{config_id}')
        
        return [TextContent(
            type="text",
            text=f"Configuration {config_id} details:\n\n" + json.dumps(data, indent=2)
        )]

    async def _create_configuration(self, args: dict):
        """Create new configuration"""
        payload = {
            "data": {
                "type": "configurations",
                "attributes": {
                    "organization-id": args['organization_id'],
                    "name": args['name'],
                    "configuration-type-id": args['configuration_type_id']
                }
            }
        }
        
        # Add optional fields
        if 'configuration_status_id' in args:
            payload["data"]["attributes"]["configuration-status-id"] = args['configuration_status_id']
        if 'notes' in args:
            payload["data"]["attributes"]["notes"] = args['notes']
        if 'serial_number' in args:
            payload["data"]["attributes"]["serial-number"] = args['serial_number']
        if 'asset_tag' in args:
            payload["data"]["attributes"]["asset-tag"] = args['asset_tag']
            
        data = self._make_request('POST', '/configurations', data=payload)
        
        return [TextContent(
            type="text",
            text=f"Successfully created configuration:\n\n" + json.dumps(data, indent=2)
        )]

    async def _list_configuration_types(self, args: dict):
        """List all configuration types"""
        data = self._make_request('GET', '/configuration_types')
        
        return [TextContent(
            type="text",
            text=f"Found {len(data.get('data', []))} configuration types:\n\n" + 
                 json.dumps(data, indent=2)
        )]

    # Flexible Asset Methods
    async def _list_flexible_assets(self, args: dict):
        """List flexible assets with optional filtering"""
        params = {}
        
        if 'organization_id' in args:
            params['filter[organization_id]'] = args['organization_id']
        if 'flexible_asset_type_id' in args:
            params['filter[flexible_asset_type_id]'] = args['flexible_asset_type_id']
            
        if 'filter' in args and args['filter']:
            for key, value in args['filter'].items():
                params[f'filter[{key}]'] = value
                
        if 'sort' in args:
            params['sort'] = args['sort']
            
        params['page[size]'] = args.get('page_size', 50)
        
        data = self._make_request('GET', '/flexible_assets', params=params)
        
        return [TextContent(
            type="text",
            text=f"Found {len(data.get('data', []))} flexible assets:\n\n" + 
                 json.dumps(data, indent=2)
        )]

    async def _get_flexible_asset(self, args: dict):
        """Get specific flexible asset by ID"""
        asset_id = args['flexible_asset_id']
        data = self._make_request('GET', f'/flexible_assets/{asset_id}')
        
        return [TextContent(
            type="text",
            text=f"Flexible asset {asset_id} details:\n\n" + json.dumps(data, indent=2)
        )]

    # Password Management Methods
    async def _list_passwords(self, args: dict):
        """List passwords with optional filtering"""
        params = {}
        
        if 'organization_id' in args:
            params['filter[organization_id]'] = args['organization_id']
            
        if 'filter' in args and args['filter']:
            for key, value in args['filter'].items():
                params[f'filter[{key}]'] = value
                
        params['page[size]'] = args.get('page_size', 50)
        
        data = self._make_request('GET', '/passwords', params=params)
        
        # Note: Actual password values are not returned in list view for security
        return [TextContent(
            type="text",
            text=f"Found {len(data.get('data', []))} password entries:\n\n" + 
                 json.dumps(data, indent=2)
        )]

    async def _get_password(self, args: dict):
        """Get specific password by ID"""
        password_id = args['password_id']
        data = self._make_request('GET', f'/passwords/{password_id}')
        
        return [TextContent(
            type="text",
            text=f"Password {password_id} details:\n\n" + json.dumps(data, indent=2)
        )]

    # Document Management Methods
    async def _list_documents(self, args: dict):
        """List documents with optional filtering"""
        params = {}
        
        if 'organization_id' in args:
            params['filter[organization_id]'] = args['organization_id']
            
        if 'filter' in args and args['filter']:
            for key, value in args['filter'].items():
                params[f'filter[{key}]'] = value
                
        if 'sort' in args:
            params['sort'] = args['sort']
            
        params['page[size]'] = args.get('page_size', 50)
        
        data = self._make_request('GET', '/documents', params=params)
        
        return [TextContent(
            type="text",
            text=f"Found {len(data.get('data', []))} documents:\n\n" + 
                 json.dumps(data, indent=2)
        )]

    async def _get_document(self, args: dict):
        """Get specific document by ID"""
        doc_id = args['document_id']
        data = self._make_request('GET', f'/documents/{doc_id}')
        
        return [TextContent(
            type="text",
            text=f"Document {doc_id} details:\n\n" + json.dumps(data, indent=2)
        )]

    # Contact Management Methods
    async def _list_contacts(self, args: dict):
        """List contacts with optional filtering"""
        params = {}
        
        if 'organization_id' in args:
            params['filter[organization_id]'] = args['organization_id']
            
        if 'filter' in args and args['filter']:
            for key, value in args['filter'].items():
                params[f'filter[{key}]'] = value
                
        if 'sort' in args:
            params['sort'] = args['sort']
            
        params['page[size]'] = args.get('page_size', 50)
        
        data = self._make_request('GET', '/contacts', params=params)
        
        return [TextContent(
            type="text",
            text=f"Found {len(data.get('data', []))} contacts:\n\n" + 
                 json.dumps(data, indent=2)
        )]

    async def _get_contact(self, args: dict):
        """Get specific contact by ID"""
        contact_id = args['contact_id']
        data = self._make_request('GET', f'/contacts/{contact_id}')
        
        return [TextContent(
            type="text",
            text=f"Contact {contact_id} details:\n\n" + json.dumps(data, indent=2)
        )]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as streams:
            await self.server.run(
                streams[0], streams[1], self.server.create_initialization_options()
            )

def main():
    """Main entry point"""
    try:
        server = ITGlueServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("Server interrupted")
    except Exception as e:
        print(f"Server error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
