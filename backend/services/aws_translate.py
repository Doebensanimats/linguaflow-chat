import boto3
from config import AWS_REGION

client = boto3.client("translate", region_name=AWS_REGION)

def translate_text(text, source_lang, target_lang):
    res = client.translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang
    )
    return res["TranslatedText"]