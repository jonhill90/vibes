# IT Glue MCP Server 📋

IT Glue MCP (Model Context Protocol) server that provides Claude with comprehensive access to IT Glue's ITSM and documentation platform.

## Features

- **Organization Management**: Create, read, update organizations and their details
- **Configuration Management**: Manage IT configurations and configuration types  
- **Asset Management**: Handle flexible assets and their relationships
- **Password Management**: Secure password storage and retrieval
- **Documentation**: Manage IT documentation and knowledge base
- **Contact Management**: Handle contact information and relationships
- **Advanced Filtering**: Comprehensive search and filtering across all resource types
- **Secure Authentication**: API key-based authentication with IT Glue
- **Rate Limiting**: Built-in awareness of IT Glue API limits
- **Comprehensive Logging**: Debug and production logging support

## Installation

### Prerequisites

- Docker and Docker Compose
- IT Glue API key
- Access to IT Glue instance

### Quick Start

1. **Clone and Setup**:
```bash
cd /workspace/vibes/mcp/mcp-itglue-server
cp .env.example .env
```

2. **Configure Environment**:
Edit `.env` with your IT Glue credentials:
```bash
ITGLUE_API_KEY=your_actual_api_key_here
ITGLUE_BASE_URL=https://api.itglue.com  # Or your custom IT Glue URL
DEBUG=false
```

3. **Build and Start**:
```bash
docker-compose up -d
```

4. **Test Connection**:
```bash
docker exec -it mcp-itglue-server python3 -c "
from server import ITGlueServer
server = ITGlueServer()
print('✅ IT Glue MCP Server connected successfully!')
"
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ITGLUE_API_KEY` | IT Glue API key for authentication | - | Yes |
| `ITGLUE_BASE_URL` | IT Glue base URL | `https://api.itglue.com` | No |
| `DEBUG` | Enable debug logging | `false` | No |
| `SERVER_NAME` | MCP server name | `mcp-itglue-server` | No |

### IT Glue API Key Setup

1. Log into your IT Glue account
2. Go to Account → API Keys
3. Click "Generate API Key"  
4. Copy the generated key to your `.env` file
5. Ensure the key has appropriate permissions for your use case

## Claude Desktop Integration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "itglue": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-itglue-server", "python3", "/workspace/server.py"]
    }
  }
}
```

Restart Claude Desktop after adding the configuration.

## Available Tools

### Organization Management

- **`list_organizations`**: List all organizations with filtering
  - Filter by name, organization type, status
  - Supports pagination and sorting
  - Example: `list_organizations(filter={"name": "Acme Corp"}, page_size=20)`

- **`get_organization`**: Get specific organization details
  - Retrieve complete organization information
  - Example: `get_organization(organization_id=123)`

- **`create_organization`**: Create new organization
  - Required: name, organization_type_id
  - Optional: description, alert, organization_status_id
  - Example: `create_organization(name="New Client", organization_type_id=1)`

- **`update_organization`**: Update existing organization
  - Update any organization attributes
  - Example: `update_organization(organization_id=123, name="Updated Name")`

### Configuration Management

- **`list_configurations`**: List configurations with filtering
  - Filter by organization, type, status, contact, serial number
  - Example: `list_configurations(organization_id=123, filter={"name": "server"})`

- **`get_configuration`**: Get specific configuration details
  - Complete configuration item information
  - Example: `get_configuration(configuration_id=456)`

- **`create_configuration`**: Create new configuration item
  - Required: organization_id, name, configuration_type_id
  - Optional: status, notes, serial_number, asset_tag
  - Example: `create_configuration(organization_id=123, name="Web Server", configuration_type_id=2)`

- **`list_configuration_types`**: Get all available configuration types
  - Returns all configuration types in IT Glue
  - Example: `list_configuration_types()`

### Asset Management

- **`list_flexible_assets`**: List flexible assets with filtering
  - Filter by organization, asset type, name
  - Example: `list_flexible_assets(organization_id=123, flexible_asset_type_id=5)`

- **`get_flexible_asset`**: Get specific flexible asset details
  - Complete flexible asset information including custom fields
  - Example: `get_flexible_asset(flexible_asset_id=789)`

### Password Management

- **`list_passwords`**: List password entries (secure)
  - Filter by organization, name, username, URL
  - Note: Actual passwords not returned in list view for security
  - Example: `list_passwords(organization_id=123, filter={"name": "admin"})`

- **`get_password`**: Get specific password details
  - Complete password entry (actual password value included)
  - Use with caution - contains sensitive data
  - Example: `get_password(password_id=101)`

### Documentation Management

- **`list_documents`**: List documents with filtering
  - Filter by organization, document name
  - Example: `list_documents(organization_id=123, filter={"name": "network"})`

- **`get_document`**: Get specific document details
  - Complete document information and content
  - Example: `get_document(document_id=202)`

### Contact Management

- **`list_contacts`**: List contacts with filtering  
  - Filter by organization, name, contact type
  - Example: `list_contacts(organization_id=123, filter={"name": "John"})`

- **`get_contact`**: Get specific contact details
  - Complete contact information
  - Example: `get_contact(contact_id=303)`

## Usage Examples

### Quick Organization Overview
```
Use list_organizations to get all clients, then get_organization for specific details on our main client.
```

### Asset Discovery
```  
First list_configurations for organization 123 to see all their IT assets, then get_configuration on any servers to see detailed specs.
```

### Password Retrieval
```
Find the admin password for client XYZ by using list_passwords with organization filter, then get_password for the specific entry.
```

### Documentation Search
```
Search for network documentation across all organizations using list_documents with name filter "network".
```

### Contact Information
```
Get all contacts for organization 456 using list_contacts, then get detailed info with get_contact.
```

## API Coverage

This MCP server implements the following IT Glue API endpoints:

### Core Resources
- ✅ Organizations (list, get, create, update)
- ✅ Configurations (list, get, create)
- ✅ Configuration Types (list)
- ✅ Flexible Assets (list, get)
- ✅ Passwords (list, get) - with security considerations
- ✅ Documents (list, get)
- ✅ Contacts (list, get)

### Advanced Features
- ✅ Comprehensive filtering and pagination
- ✅ Sorting support where available
- ✅ Proper error handling and logging
- ✅ Rate limiting awareness
- ✅ Secure password handling

### Future Enhancements (Not Yet Implemented)
- ⏳ Create/Update for flexible assets, passwords, documents, contacts
- ⏳ Bulk operations support
- ⏳ Relationship management between items
- ⏳ File attachment handling
- ⏳ Advanced search across multiple resource types
- ⏳ Audit trail integration
- ⏳ Data export capabilities (JSON, CSV)

## Security Considerations

### API Key Protection
- Never log API keys in plain text
- Store API keys in environment variables only
- Use `.env` files for local development (never commit to version control)

### Password Management  
- Password values are only returned in `get_password` calls
- List operations return metadata only for security
- Always verify user authorization before retrieving passwords
- Consider logging password access for audit purposes

### Data Handling
- All API communications use HTTPS
- Input validation prevents injection attacks  
- Error messages don't expose sensitive system information
- Debug logs can be disabled in production

## Troubleshooting

### Common Issues

**Authentication Failed**
```
Error: Invalid IT Glue API key
```
- Verify API key in `.env` file
- Check API key permissions in IT Glue
- Ensure API key hasn't expired

**Connection Timeout**
```
Error: IT Glue API Request Failed: timeout
```
- Check ITGLUE_BASE_URL is correct
- Verify network connectivity to IT Glue
- Check IT Glue service status

**Rate Limiting**
```
Error: HTTP 429 Too Many Requests
```
- IT Glue has API rate limits
- Implement delays between bulk operations
- Consider upgrading IT Glue plan for higher limits

### Debug Mode

Enable debug logging:
```bash
DEBUG=true docker-compose up -d
```

View detailed logs:
```bash
docker logs -f mcp-itglue-server
```

### Health Check

Test server connectivity:
```bash
docker exec -it mcp-itglue-server python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
headers = {'x-api-key': os.getenv('ITGLUE_API_KEY'), 'Content-Type': 'application/vnd.api+json'}
resp = requests.get(f\"{os.getenv('ITGLUE_BASE_URL', 'https://api.itglue.com')}/organizations\", headers=headers)
print(f'Status: {resp.status_code} - {\"✅ Connected\" if resp.status_code == 200 else \"❌ Failed\"}')
"
```

## Development

### Local Development Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**:
```bash
export ITGLUE_API_KEY="your_api_key"
export ITGLUE_BASE_URL="https://api.itglue.com"  
export DEBUG="true"
```

3. **Run Server**:
```bash
python3 server.py
```

### Adding New Tools

1. Add tool definition to `list_tools()` method
2. Add handler method (e.g., `_new_tool_handler`)
3. Add case to `call_tool()` method
4. Update documentation and tests

### Testing

Basic functionality test:
```bash
python3 -c "
from server import ITGlueServer
import asyncio

async def test():
    server = ITGlueServer()
    result = await server._list_organizations({})
    print('Test passed!' if result else 'Test failed!')

asyncio.run(test())
"
```

## License

This MCP server is part of the Vibes MCP ecosystem. See the main Vibes repository for license information.

## Support

- Check IT Glue API documentation: https://api.itglue.com/developer/
- Review Vibes MCP server patterns for consistency
- Open issues in the main Vibes repository for bugs or feature requests

---

**Note**: This server provides read access and basic create/update operations for IT Glue resources. Always test in a development environment before using in production, and ensure proper backup procedures are in place when performing write operations.
