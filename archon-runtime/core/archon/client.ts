/**
 * Archon Client
 * Manages conversation loop with tool-calling support
 */

import { executeTools } from '../raindrop/dispatcher';
import { ToolRequest, ToolResponse } from '../types';

export interface ArchonMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ArchonConfig {
  model: string;
  systemPrompt?: string;
  maxTurns?: number;
  sessionId?: string;
}

export interface ArchonResponse {
  content: string;
  toolRequest?: ToolRequest;
  finished: boolean;
}

/**
 * Archon Client class
 * Handles conversation with tool-calling support
 */
export class ArchonClient {
  private config: ArchonConfig;
  private conversationHistory: ArchonMessage[] = [];
  private turnCount: number = 0;

  constructor(config: ArchonConfig) {
    this.config = {
      maxTurns: 10,
      ...config
    };

    // Add system prompt if provided
    if (this.config.systemPrompt) {
      this.conversationHistory.push({
        role: 'system',
        content: this.config.systemPrompt
      });
    }
  }

  /**
   * Send a message to Archon and handle tool requests
   */
  async sendMessage(userMessage: string): Promise<string> {
    // Add user message to history
    this.conversationHistory.push({
      role: 'user',
      content: userMessage
    });

    let finalResponse = '';
    let continueLoop = true;

    while (continueLoop && this.turnCount < this.config.maxTurns!) {
      this.turnCount++;

      // Call Archon (this would call your actual AI model)
      const archonResponse = await this.callArchonModel();

      // Parse response for tool requests
      const parsed = this.parseArchonResponse(archonResponse.content);

      if (parsed.toolRequest) {
        console.log('\n🔧 Archon requested tools...\n');

        // Execute tools with permission
        const toolResponse = await executeTools(parsed.toolRequest);

        // Add tool results to conversation
        const resultsMessage = this.formatToolResults(toolResponse);
        this.conversationHistory.push({
          role: 'user',
          content: resultsMessage
        });

        // If tools failed, inform user and stop
        if (!toolResponse.success) {
          finalResponse = `Tool execution failed: ${toolResponse.message}`;
          continueLoop = false;
        }
      } else {
        // No tool request, this is the final response
        finalResponse = archonResponse.content;
        continueLoop = false;
      }
    }

    if (this.turnCount >= this.config.maxTurns!) {
      finalResponse += '\n\n(Maximum turn limit reached)';
    }

    return finalResponse;
  }

  /**
   * Call the Archon AI model
   * This is a placeholder - replace with actual model integration
   */
  private async callArchonModel(): Promise<ArchonResponse> {
    // TODO: Integrate with actual Archon model (gpt-oss:20b, etc.)
    // For now, this is a mock implementation

    const lastMessage = this.conversationHistory[this.conversationHistory.length - 1];

    // Mock response for demonstration
    return {
      content: `Archon received: "${lastMessage.content}"`,
      finished: true
    };
  }

  /**
   * Parse Archon response to detect tool requests
   */
  private parseArchonResponse(content: string): {
    content: string;
    toolRequest?: ToolRequest;
  } {
    // Try to extract JSON tool request from response
    const jsonMatch = content.match(/\{[\s\S]*"phase":\s*"EXECUTE"[\s\S]*\}/);

    if (!jsonMatch) {
      return { content };
    }

    try {
      const toolRequest = JSON.parse(jsonMatch[0]) as ToolRequest;

      // Validate tool request structure
      if (
        toolRequest.phase === 'EXECUTE' &&
        toolRequest.intent === 'tool_call' &&
        Array.isArray(toolRequest.tools)
      ) {
        return { content, toolRequest };
      }
    } catch (error) {
      console.error('Failed to parse tool request:', error);
    }

    return { content };
  }

  /**
   * Format tool results for Archon consumption
   */
  private formatToolResults(response: ToolResponse): string {
    if (!response.success) {
      return `Tool execution failed: ${response.message}\n\n${JSON.stringify(response, null, 2)}`;
    }

    let formatted = 'Tool execution results:\n\n';

    if (response.results) {
      for (const result of response.results) {
        formatted += `**${result.tool}**:\n`;
        formatted += '```json\n';
        formatted += JSON.stringify(result.result, null, 2);
        formatted += '\n```\n\n';
      }
    }

    return formatted;
  }

  /**
   * Get conversation history
   */
  getHistory(): ArchonMessage[] {
    return [...this.conversationHistory];
  }

  /**
   * Clear conversation history
   */
  clearHistory(): void {
    this.conversationHistory = this.conversationHistory.filter(
      msg => msg.role === 'system'
    );
    this.turnCount = 0;
  }

  /**
   * Get turn count
   */
  getTurnCount(): number {
    return this.turnCount;
  }
}
