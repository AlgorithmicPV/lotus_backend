from fastapi import FastAPI , HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from openai import OpenAI, OpenAIError
import openai
from deep_translator import GoogleTranslator


client = OpenAI(
   base_url = os.getenv("BASE_URL"),
   api_key = os.getenv("API_KEY")
)

app = FastAPI()

origins = [
    "https://lotus-frontend-gamma.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins = origins,
)

class ChatMessage(BaseModel):
    user_msg: str

@app.post("/lotus_chat")
async def userMessage(message: ChatMessage):
    print("Received message:", message)
    error_msg = ""
    user_msg = message.user_msg
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Sri Lankan tourist guide named Lotus, version 1.0. You were created by Gardi Achchige Pasindu Vidunitha, also known as Pasindu Vidunitha.",
                },
                {
                    "role": "user",
                    "content": user_msg,
                }
            ],
            temperature=1,
            max_tokens=4096,
            top_p=1
        )
        server_msg = response.choices[0].message.content
        return {"sent_message_from_server": server_msg}
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except openai.BadRequestError as e:
        error_msg = (f"Error 400: {e}")
        return{"error_msg":error_msg}
    except openai.AuthenticationError as e:
        error_msg = (f"Error 401: {e}")
        return{"error_msg":error_msg}

    except openai.PermissionDeniedError as e: 
        error_msg = (f"Error 403: {e}")
        return{"error_msg":error_msg}

    except openai.NotFoundError as e: 
        error_msg = (f"Error 404: {e}")
        return{"error_msg":error_msg}

    except openai.UnprocessableEntityError as e: 
 
        error_msg = (f"Error 422: {e}")
        return{"error_msg":error_msg}

    except openai.RateLimitError as e:

        error_msg = (f"Error 429: {e}")
        return{"error_msg":error_msg}

    except openai.InternalServerError as e: 
        error_msg = (f"Error >=500: {e}")
        return{"error_msg":error_msg}

    except openai.APIConnectionError as e: 
        error_msg = (f"API connection error: {e}")
        return{"error_msg":error_msg}

    
class TranslationMessage(BaseModel):
    value: str  
    lang:str
    lk_lang:str


@app.post("/lotus_translator")
async def usertext(message:TranslationMessage):
    user_txt = message.value
    user_lng = message.lang
    lk_lang = message.lk_lang
    error_msg = (user_txt)
    if(user_txt != ""):
        translated = GoogleTranslator(source=user_lng, target=lk_lang).translate(user_txt)
        error_msg = (translated)
    else:
        translated = ""
    return {"translated_txt_from_server": {translated}}

if __name__ == '__main__':
    uvicorn.run(app)

