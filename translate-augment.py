from google.cloud import translate
import os
import pandas as pd
import datetime
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\sg\\nlp\clinical-sts\clinical-sts-c2e7c539a15e.json'
project_id="clinical-sts"

lang = "en-US"
mid_lang  = "fr"
train_file = "data\\augmented_train_encoded.tsv"

def translate_text(text="YOUR_TEXT_TO_TRANSLATE", source_lang="en-uS", target_lang="en-uS"):
        
    """Translating Text."""

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    
    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": source_lang,
            "target_language_code": target_lang,
        }
    )

    return response
def augment(text):
    resp = translate_text(text, lang, mid_lang)
    resp2 = translate_text(resp.translations[0].translated_text, mid_lang, lang)
    # print("\n",text,"\n")
    # print(resp.translations[0].translated_text,"\n")
    # print(resp2.translations[0].translated_text,"\n")
    return resp2.translations[0].translated_text

def append_new_samples(train_file):

    df1 = pd.read_csv(train_file, sep="\t", names=["sentence_1", "sentence_2", "similarity_score", "label"], encoding="utf-8")
    df2 = df1.copy()
    for i,row in df1.iterrows():
        aug1 = augment(row["sentence_1"])
        aug2 = augment(row["sentence_2"])
        new_row = [aug1, aug2, row["similarity_score"], row["label"]]
        df2.loc[len(df2)] = new_row    
        if i%10==3:
            print("At row", i)
    print("\n\nSize of old file",df1.shape)
    print("Size of new file",df2.shape)
    new_file= os.path.splitext(train_file)[0] + "_translate_" + datetime.datetime.today().strftime('%m-%d_%H-%M')+".tsv"

    df2.to_csv(new_file, sep='\t', encoding='utf-8', index=False, header=None)


if __name__ == "__main__":
    append_new_samples(train_file)