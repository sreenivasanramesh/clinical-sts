# Ran the following commands prior to executing this file
# cp train.txt train_copy.txt
# tr '[:upper:]' '[:lower:]' < train_copy.txt > tempfile && mv tempfile train_copy.txt
# tr '[:punct:]' ' ' < train_copy.txt > tempfile && mv tempfile train_copy.txt
# tr '\t' ' ' < train_copy.txt > tempfile && mv tempfile train_copy.txt
# tr -s ' ' < train_copy.txt > tempfile && mv tempfile train_copy.txt
#
# nohup perl -Mopen=locale -Mutf8 -lpe '
# BEGIN{open(A,"stopwords-google-10000-english.txt"); chomp(@k = <A>)}
# for $w (@k){s/(^|[ ,.—_;-])\Q$w\E([ ,.—_;-]|$)/$1$2/ig}' train_copy.txt > parsed_train_text.txt &
#
# tr -s ' ' < parsed_train_text.txt > tempfile && mv tempfile parsed_train_text.txt
# tr '\t' ' ' < parsed_train_text.txt > tempfile && mv tempfile parsed_train_text.txt

import requests
import json
import time

non_drug_words = set()
drug_names = set()


rate_counter = 0
def is_drug(word):
    if word in drug_names:
        return True
    if word in non_drug_words:
        return False
    global rate_counter
    rate_counter += 1
    if rate_counter % 15 == 0:
        time.sleep(1.5)
    url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json?drugName={}&relaSource=MEDRT&relas=may_treat".format(word)
    response = json.loads(requests.get(url).text)
    if "rxclassDrugInfoList" in response:
        drug_names.add(word)
        return True
    else:
        non_drug_words.add(word)
    return False


def get_drug_mentions(data_sample):
    count = 0
    for word in data_sample.lstrip().split():
        if word.isdigit() or len(word) < 4:
            continue
        if is_drug(word):
            count += 1
    return count



def main():

    with open('data/parsed_train_text.txt') as parsed_file:
        data = parsed_file.read().splitlines()

    # get drug mention count
    for data_sample in data:
        count = str(get_drug_mentions(data_sample))
        with open('/Users/vasan/clinical-sts/data/drug_mentions_per_sample.txt', mode='a', encoding='utf-8') as count_file:
            count_file.write(count+"\n")

    # append convert drug mention counts to labels and append to original dataset
    with open('data/train.txt') as data_file, \
         open('/Users/vasan/clinical-sts/data/drug_mentions_per_sample.txt') as data_sample:
        for sample, drug_count in zip(data_file, data_sample):
            class_label = "MANUAL"
            drug_count = int(drug_count.strip())
            if drug_count > 1:
                class_label = "MEDICAL"
            elif drug_count == 1:
                if (sub_str in sample for sub_str in ["TAB", "tablet", "capsule", "times a day", "times daily", "times as", "by mouth", "as needed"]):
                    class_label = "MEDICAL"
            elif drug_count == 0:
                class_label = "CLINICAL"

            with open('/Users/vasan/clinical-sts/data/augmented_train.tsv', mode='a', encoding='utf-8') as augumented_data_file:
                augumented_data_file.write(sample.replace("\n", "") + "\t" + class_label + "\n")


main()

