import google.generativeai as genai

class Genai:
    def __init__(self, genai_api_key: str, model_name: str):
        if not genai_api_key:
            raise ValueError("Gemini API key cannot be empty or None")
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel(model_name)

    def convert_to_natural_instructions(self, instructions):
        """Convert technical instructions to natural voice-like navigation"""
        instructions_text = "\n".join(
            [f"{i+1}. {step['text']} ({step['distance']}m)" for i, step in enumerate(instructions[:10])]
        )

        prompt = (
            "Convert these technical navigation instructions to natural, voice-like navigation:\n"
            f"{instructions_text}\n\nMake them sound like a friendly GPS voice. Keep each instruction concise."
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text.split('\n')
        except Exception as e:
            return [f"Unable to generate voice instructions: {str(e)}"]

    def generate_route_summary(self, paths_data, origin, destination, vehicle):
        """Generate a natural language summary of the route using Gemini"""
        distance = paths_data["paths"][0]["distance"] / 1000
        duration = paths_data["paths"][0]["time"] / (1000 * 60)

        key_points = [step["text"] for step in paths_data["paths"][0]["instructions"][:5]]
        prompt = (
            f"Summarize a {vehicle} route from {origin} to {destination}. "
            f"Distance: {distance:.1f}km, Duration: {duration:.0f} minutes. "
            f"Key instructions: {', '.join(key_points[:3])}."
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error generating summary: {str(e)}"

    def parse_natural_language_input(self, input_text):
        """Convert natural language input into structured location data using Gemini"""
        prompt = f"Extract specific location information from: '{input_text}' and return it as a JSON object."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error parsing input: {str(e)}"

    def find_accommodations(self, destination):
        prompt = f"Can you recommend me any acomondation in Pinkafeld, no need for any specification! Just list me 3 accomodations in '{destination}' without any context in this format: Accomondation1, Accomondation2, Accomondation3"
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error parsing input: {str(e)}"
