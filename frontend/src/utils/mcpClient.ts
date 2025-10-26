/**
 * MCP Client using the official @modelcontextprotocol/sdk
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

class RestaurantMCPClient {
  private client: Client | null = null;
  private transport: SSEClientTransport | null = null;
  private connectionPromise: Promise<void> | null = null;
  private serverUrl: string;

  constructor(serverUrl: string = 'http://localhost:8001/sse') {
    this.serverUrl = serverUrl;
  }

  /**
   * Connect to the MCP server
   */
  async connect(): Promise<void> {
    // If already connecting, wait for that connection
    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    // If already connected, return immediately
    if (this.client) {
      return Promise.resolve();
    }

    this.connectionPromise = (async () => {
      try {
        console.log('[MCP] Connecting to server:', this.serverUrl);

        // Initialize the client
        this.client = new Client(
          {
            name: "restaurant-frontend-client",
            version: "1.0.0",
          },
          {
            capabilities: {},
          }
        );

        // Create SSE transport pointing to the server
        this.transport = new SSEClientTransport(new URL(this.serverUrl));

        // Connect to the server
        await this.client.connect(this.transport);
        console.log('[MCP] Connected to Restaurant MCP Server');
      } catch (error) {
        console.error('[MCP] Connection failed:', error);
        this.client = null;
        this.transport = null;
        this.connectionPromise = null;
        throw error;
      }
    })();

    return this.connectionPromise;
  }

  /**
   * Call an MCP tool
   */
  async callTool(toolName: string, args: Record<string, any> = {}): Promise<any> {
    // Ensure we're connected
    await this.connect();

    if (!this.client) {
      throw new Error('MCP client not connected');
    }

    try {
      console.log(`[MCP] Calling tool: ${toolName}`, args);

      // Try calling the tool directly first (FastMCP might not use server prefix)
      const result = await this.client.callTool({
        name: toolName,
        arguments: args,
      });

      console.log(`[MCP] Tool result:`, result);

      // Check if the result is an error
      if (result.isError) {
        const errorText = result.content?.[0]?.text || 'Unknown error';
        throw new Error(errorText);
      }

      // Parse the result - MCP returns content array with text
      if (result.content && result.content.length > 0) {
        const text = result.content[0].text;
        return typeof text === 'string' ? JSON.parse(text) : text;
      }

      return result;
    } catch (error) {
      console.error(`[MCP] Tool call failed for ${toolName}:`, error);
      throw error;
    }
  }

  /**
   * Disconnect from the server
   */
  async disconnect(): Promise<void> {
    if (this.client) {
      await this.client.close();
      this.client = null;
      this.transport = null;
      this.connectionPromise = null;
      console.log('[MCP] Disconnected from server');
    }
  }
}

// Export singleton instance
// Use the Vite proxy URL to avoid CORS issues
// In dev: http://localhost:3000/api/sse -> http://localhost:8001/sse
const sseUrl = window.location.origin + '/api/sse';
export const mcpClient = new RestaurantMCPClient(sseUrl);

// Export helper function for calling tools
export async function callMCPTool(toolName: string, args: Record<string, any> = {}): Promise<any> {
  return await mcpClient.callTool(toolName, args);
}
