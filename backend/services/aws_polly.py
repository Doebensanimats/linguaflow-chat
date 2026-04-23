import boto3
from config import AWS_REGION

polly = boto3.client("polly", region_name=AWS_REGION)

def text_to_speech(text, lang="en"):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Joanna"
    )
    return response["AudioStream"].read()