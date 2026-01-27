import logging
import google.generativeai as genai
from backend.core.config import settings

logger = logging.getLogger(__name__)

class SummaryService:
    def summarize(self, text: str, api_key: str = None) -> str:
        api_key = api_key or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("Gemini API Key is required for summarization (env: GEMINI_API_KEY)")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash for speed and long context
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
You are an expert content summarizer. Please summarize the following transcript from a YouTube video into a comprehensive Markdown note.

**Requirements:**
1.  **Title**: Create a catchy and descriptive title suitable for the content.
2.  **Summary**: A brief executive summary (3-5 sentences).
3.  **Key Takeaways**: Bullet points of the most important concepts.
4.  **Detailed Notes**: Organize the content into logical sections with clear headings. Use sub-bullets to capture details.
5.  **Quality**: Improve the readability. The input is a raw transcript, so fix grammar, remove filler words, and ensure coherence.
6.  **Language**: Output in Traditional Chinese (繁體中文).
7.  **Mind Map**: Create a MermaidJS mindmap code block (`mermaid`) summarizing the core structure of the video. 
    **CRITICAL**: The code block MUST start with the specific keyword `mindmap` on the first line. Do not use `graph TD`.
    Example:
    ```mermaid
    mindmap
      Root((Main Title))
        Topic A
          Detail 1
          Detail 2
        Topic B
    ```

**Transcript:**
{text}
"""
        
        logger.info("Sending request to Gemini 1.5 Flash...")
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            raise RuntimeError(f"Failed to generate summary: {str(e)}")
