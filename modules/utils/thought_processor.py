from ai_providers.multi_provider import MultiProvider

class ThoughtProcessor:
    def __init__(self, ai_provider=None):
        """Initialize with optional AI provider, otherwise use Multi-provider"""
        self.ai_provider = ai_provider if ai_provider else MultiProvider()
        
        # Add initial learning context
        if isinstance(self.ai_provider, MultiProvider):
            self.ai_provider.add_learning_context("role", "You are a helpful thought processor that helps organize and improve ideas")
            self.ai_provider.add_learning_context("style", "Clear, structured, and always building on previous context")
            self.ai_provider.add_learning_context("goal", "Help refine and develop the user's thoughts over multiple interactions")

    def process_thoughts(self, raw_thoughts):
        """Process raw thoughts into three different formats"""
        try:
            # Create prompts for different formats
            structured_prompt = f"""Convert these thoughts into clear, structured content. Follow these rules:
            1. Break the content into clear sections
            2. Use bullet points for key ideas
            3. Keep the original meaning but make it organized
            4. Add a brief summary at the top
            5. Build on any previous context to show deeper understanding
            
            Here are the thoughts to structure:
            {raw_thoughts}"""
            
            powerful_prompt = f"""Transform these thoughts into powerful, direct content. Make it:
            1. Bold and impactful
            2. No holding back
            3. Clear and direct
            4. Emotionally engaging
            5. Use previous context to make it more compelling
            
            Here are the thoughts to transform:
            {raw_thoughts}"""
            
            template_prompt = f"""Create a kind but strong response to these thoughts. Make it:
            1. Empathetic and understanding
            2. Supportive but firm
            3. Clear point of view
            4. Constructive and helpful
            5. Reference previous interactions to show understanding
            
            Here are the thoughts to respond to:
            {raw_thoughts}"""
            
            # Get responses using specialized providers
            structured = self.ai_provider.generate_response(structured_prompt, style="structured")
            powerful = self.ai_provider.generate_response(powerful_prompt, style="powerful")
            template = self.ai_provider.generate_response(template_prompt, style="empathetic")
            
            return {
                "structured": structured,
                "powerful": powerful,
                "template": template
            }
            
        except Exception as e:
            return {
                "structured": f"Error processing thoughts: {str(e)}",
                "powerful": f"Error processing thoughts: {str(e)}",
                "template": f"Error processing thoughts: {str(e)}"
            }
            
    def clear_learning(self):
        """Clear any stored learning context"""
        if isinstance(self.ai_provider, MultiProvider):
            self.ai_provider.clear_learning_context()
