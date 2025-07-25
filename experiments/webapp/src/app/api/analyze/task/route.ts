import { NextRequest } from 'next/server';

import { TaskAnalysisSchema, TaskAnalysisRequestSchema } from '@/types'
import { azureChatCompletion } from '@/utils/azure-client';

export async function POST(req: NextRequest) {
  try {
    const body = TaskAnalysisRequestSchema.parse(await req.json());
    const { task, model, temperature } = body;

    // Create analysis prompt
    const systemPrompt = `You are an expert AI evaluator analyzing why an AI agent succeeded or failed at a task. 

Your job is to analyze the conversation between a user and an AI agent, along with the final answer and score, to understand what went wrong (or right).

Please provide your analysis in the following JSON format:
{
  "reason": "A clear, detailed explanation of why the task failed or succeeded",
  "suggestion": "Actionable suggestions on how to improve the task execution if it failed"
}

Constraints of the system:
- Fully autonomous. The agent is _never_ allowed to talk to the user.

Be specific and actionable in your analysis, but do not violate any of the contraints.`;

    const userPrompt = `Analyze this AI agent task execution:

**Final Score:** ${task.score.score} (1 = success, 0 = failure)

**Final Answer:** ${task.answer.answer}

**Conversation Messages:**
${task.messages.map((msg, idx) =>
      `${idx + 1}. **${msg.source.toUpperCase()}**: ${msg.content}
`).join('')}

Please analyze why this task ${task.score.score === 1 ? 'succeeded' : 'failed'} and provide your assessment in the requested JSON format.`;

    const response = await azureChatCompletion(model, [
      { role: "system", content: systemPrompt },
      { role: "user", content: userPrompt }
    ], {
      temperature: temperature
    });

    const text = response.choices[0]?.message?.content;
    if (!text) {
      throw new Error('No response content from Azure API');
    }

    const jsonMatch = text.match(/{[\s\S]*}/);
    if (!jsonMatch) {
      throw new Error('No JSON object found in analysis response');
    }
    const jsonText = jsonMatch[0];
    const result = TaskAnalysisSchema.parse({ taskId: task.taskId, ...JSON.parse(jsonText) });

    return Response.json(result);

  } catch (error) {
    console.error('Analysis API error:', error);
    return Response.json(
      { error: 'Failed to analyze task', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
