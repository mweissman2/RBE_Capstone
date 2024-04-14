import google.generativeai as genai
from Communication import utils
from PIL import Image
import random
import glob


def get_image(folder_path):
    """
  To be replaced with actual get_image in the future
  Right now, just returns a random image in a given folder
  """
    file_names = glob.glob(f"{folder_path}/*.jpg")
    if file_names:
        random_image = Image.open(random.choice(file_names))
        return random_image
    else:
        print("No images found")
        return None  # No JPEGs found


def describe_image_short(img: Image):
    print("Image captioning starting")
    img.show()

    # Perform response refinement here
    API_KEY = utils.get_key("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

    # Model configuration
    generation_config = genai.types.GenerationConfig(
        temperature=0.5,
        top_p=1,
        top_k=1,
        max_output_tokens=512,
    )

    safety_settings = utils.set_gemini_safety_settings()

    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    prompt = "Only describe the most important objects in the image and the overall scene. Keep your response concise."

    response = model.generate_content([prompt, img])
    print(f"Image Caption: {response.text}")

    return response.text

def describe_image(img: Image):
    print("Image captioning starting")
    img.show()

    # Perform response refinement here
    API_KEY = utils.get_key("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

    # Model configuration
    generation_config = genai.types.GenerationConfig(
        temperature=0.9,
        top_p=1,
        top_k=1,
        max_output_tokens=2048,
    )

    safety_settings = utils.set_gemini_safety_settings()

    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  # generation_config=generation_config,
                                  safety_settings=safety_settings)

    prompt = "Imagine you are the camera, focus on describing all objects in the image and their relative location to " \
             "the camera. Make sure to mention if an object is moving towards or away from the camera. Be concise."

    response = model.generate_content([prompt, img])
    print(f"Image Caption: {response.text}")

    return response.text

def few_shot_describe_image(img: Image):
    content = []
    img3 = Image.open('Communication/imgs/img3.jpg')
    img4 = Image.open('Communication/imgs/img4.jpg')
    prompt3 = "sidewalk: [stationary, straight], street: [stationary, right], tree: [stationary, right], cars: [stationary, right], cyclists: [moving, away_from_cam, right]"
    prompt4 = "sidewalk: [stationary, straight], street: [stationary, right], lawn: [stationary, left], cactus: [stationary, left], pedestrian: [moving, away_from_cam, straight]"
    content.append(img3)
    content.append(prompt3)
    content.append(img4)
    content.append(prompt4)
    content.append(img)

    img.show()

    # Perform response refinement here
    API_KEY = utils.get_key("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

    # Model configuration
    generation_config = genai.types.GenerationConfig(
        temperature=0.9,
        top_p=1,
        top_k=1,
        max_output_tokens=2048,
    )

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "block_none"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  # generation_config=generation_config,
                                  safety_settings=safety_settings)

    content.append("Follow the format of the previous prompts, use left when the object is on the left of the "
                   "image, right when the object is on the right. If an object is moving, make sure to add the "
                   "direction (moving away or towards camera). Keep your response concise")

    response = model.generate_content(content)
    print(response.text)

    return response.text
