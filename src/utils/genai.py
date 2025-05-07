import google.generativeai as genai
import json

class Genai:
    """
    Provides functionalities for generating natural language instructions and summaries,
    parsing natural language inputs, finding accommodations, planning public transportation
    routes, and analyzing weather impacts on trips. This class interacts with the
    Gemini Generative Model API for processing and generating outputs.

    Attributes:
        model: An instance of Gemini's GenerativeModel configured with the specified model name.

    Methods:
        None
    """
    def __init__(self, genai_api_key: str, model_name: str):
        if not genai_api_key:
            raise ValueError("Gemini API key cannot be empty or None")
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel(model_name)

    def convert_to_natural_instructions(self, instructions):
        """
        Converts a list of technical navigation instructions into a more natural and friendly, voice-like format.

        This function takes navigation instructions, potentially containing distances, and constructs a prompt
        to generate improved voice navigation directions using an external model. The output is a set of concise
        and human-friendly voice instructions.

        Parameters:
        instructions: list
            List of navigation instructions. Each instruction is expected to be a dictionary
            containing a 'text' key representing the instruction details, and optionally a
            'distance' key for the corresponding distance in meters.

        Returns:
        list
            A list of natural voice-like navigation instructions. If an error occurs during
            the instruction generation process, a single-element list containing an error
            message is returned.
        """
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
        """
        Summarizes a transportation route based on provided path data.

        This method processes route information such as distance, duration, and key
        instructions, then generates a summary of the route using a language
        generation model. The summary includes details like the type of vehicle,
        origin, destination, and key instructions for navigation.

        Parameters:
            paths_data (dict): Dictionary containing paths and instruction details.
            origin (str): The starting point of the route.
            destination (str): The endpoint of the route.
            vehicle (str): The type of vehicle for the route (e.g., car, bike).

        Returns:
            str: A generated textual summary of the route based on the provided
                 data.
        """
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
        """
        Parses natural language input to extract specific location information and returns
        the extracted data as a JSON object.

        Parameters:
        input_text : str
            The natural language text input containing location information to be parsed.

        Returns:
        str
            A JSON-formatted string containing extracted location information from the input text
            or an error message if parsing fails.
        """
        prompt = f"Extract specific location information from: '{input_text}' and return it as a JSON object."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error parsing input: {str(e)}"

    def find_accommodations(self, destination):
        """
        Finds and recommends accommodations for a specified destination.

        This method generates a prompt using the provided destination and interacts
        with an external model to retrieve accommodation recommendations in the
        English language. The recommendations are returned in a simple
        comma-separated format without any additional context.

        Args:
            destination (str): The name of the destination for which to find accommodations.

        Returns:
            str: A comma-separated string listing three accommodations for the specified
            destination or an error message in case of an exception.
        """
        prompt = (f"Can you recommend me any acomondation in '{destination}', no need for any specification! Just list me 3 "
                  f"accomodations in '{destination}' without any context in English and in this format: Accomondation1, "
                  f"Accomondation2, Accomondation3")
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error parsing input: {str(e)}"

    def route_public_transportation(self, start_location, end_location, start_time):
        """
        Provides functionality to find public transportation routes between a start and end location at a specified start time.

        Parameters for methods:
            start_location: str
                The starting point for the route.
            end_location: str
                The destination point for the route.
            start_time: str
                The time to start the journey, formatted as a string.

        Raises:
            Exception
                If there is an error in parsing the API's output or generating content.

        Returns:
            tuple
                A tuple containing:
                - dict: Parsed JSON with route details and instructions.
                - int: HTTP-like status code indicating success (200) or failure.
        """
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
        """
        Analyzes weather conditions for a trip by comparing current weather in the departure
        location and the forecasted weather at the destination and generates a summary.

        Parameters:
            departure: str
                The starting location of the trip.
            destination: str
                The target location of the trip.
            travel_time: str
                The estimated duration to reach the destination.
            current_weather: str
                The current weather at the departure location.
            forecast_weather: str
                The forecasted weather at the destination after the specified travel time.

        Raises:
            Exception
                Returns an error message if `model.generate_content` fails.

        Returns:
            str
                A summary and comparison of weather conditions, or an error message upon failure.
        """
        # print(f"Current weather : {current_weather} \n Forecast weather :{forecast_weather}\n")  # debug
        prompt = (
            f"I'm planning a trip from {departure} to {destination}.\n"
            f"Current weather in {departure} is {current_weather}.\n"
            f"Forecast after the next {travel_time} in {destination} is {forecast_weather}.\n"
            f"Are there any extreme weather conditions that might affect the trip?\n "
            f"Do I need any preparation to accomadate these weather situations? \n"
            f"Don't repeat my questions. Give me a summary and a comparison. Use emojis, don't use **"
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"
