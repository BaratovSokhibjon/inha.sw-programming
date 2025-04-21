import google.generativeai as genai
import json

class Genai:
    def __init__(self, genai_api_key: str, model_name: str):
        if not genai_api_key:
            raise ValueError("Gemini API key cannot be empty or None")
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel(model_name)

    def convert_to_natural_instructions(self, instructions):
        """Convert technical instructions to natural voice-like navigation"""
        if "distance" in instructions:
            instructions_text = "\n".join(
                [f"{i + 1}. {step['text']} ({step['distance']}m)" for i, step in enumerate(instructions[:10])]
            )
        else:
            instructions_text = "\n".join(
                [f"{i + 1}. {step['text']})" for i, step in enumerate(instructions[:10])]
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
        prompt = (f"Can you recommend me any acomondation in '{destination}', no need for any specification! Just list me 3 "
                  f"accomodations in '{destination}' without any context in English and in this format: Accomondation1, "
                  f"Accomondation2, Accomondation3")
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error parsing input: {str(e)}"

    def route_public_transportation(self, start_location, end_location, start_time):
        example_json = json.dumps({"paths":[{"distance":195858.491,"weight":10526.955824,"time":7240491,"instructions":[{"distance":69.286,"heading":114.41,"sign":0,"interval":[0,1],"text":"Continue onto Singerstraße","time":15589,"street_name":"Singerstraße"},{"distance":70.162,"sign":2,"interval":[1,2],"text":"Turn right onto Liliengasse","time":15786,"street_name":"Liliengasse"}]}]})
        prompt = (f"Please tell me instructions to get from '{start_location}' to '{end_location}' starting at "
                  f"'{start_time}' only using Public Transportation! - please answer me in a proper json format having "
                  f"this points: time, distance, starting "
                  f"location, end location, paths! For distance just give me the number in meter and for time ms! Please in English! "
                  f"It should look like this:"
                  f"'{example_json}'")
        try:
            response = self.model.generate_content(prompt)
            cleaned = bytes(response.text, "utf-8").decode("unicode_escape")
            if cleaned.startswith('"') and cleaned.endswith('"'):
                cleaned = cleaned[1:-1]

            if cleaned.startswith("```json") and cleaned.endswith('```'):
                cleaned = cleaned[7:-3]

            parsed_json = json.loads(cleaned)
            paths_status = 200
            return parsed_json, paths_status
        except Exception as e:
            return f"❌ Error parsing input: {str(e)}"
        
    def check_weather_conditions(self, departure, destination, travel_time, current_weather, forecast_weather):
        print(f"Current weather : {current_weather} \n Forecast weather :{forecast_weather}\n")
        prompt = (
            f"I'm planning a trip from {departure} to {destination}.\n"
            f"Current weather in {departure} is {current_weather}.\n"
            f"Forecast after the next {travel_time} in {destination} is {forecast_weather}.\n"
            f"Are there any extreme weather conditions that might affect the trip?\n "
            f"Do I need any preparation to accomadate these weather situations? \n"
            f"Don't repeat my questions. Give me a summary and a comparison"
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"


