from pyspark.sql.functions import col

import re

def parse_atc():
    """
    Parse br08308.keg, we only keep the lines with an ATC Code
    Convert the data to a csv file
    """
    print("Generating ATC codes file...")
    with open("./data/br08303.keg", "r") as file:
        content = file.read()
        pattern = re.compile(r"[A-Z][0-9]{2}[A-Z]{2}[0-9]{2}.*\n")
        result = re.findall(pattern, content)
        for i in range(len(result)):
            result[i] = result[i].strip()
            result[i] = result[i].replace(",", "")
            result[i] = result[i].replace(" ", ",", 1)
            result[i] += "\n"
        #print(len(result))

        with open("./data/atc_codes.csv", "w") as file:
            file.write("ATCCode,Description\n")
            for item in result:
                file.write(item)
    print("Done !")

def delete_tags():
    """
    Delete the tags like [DG:DG00001] on some lines
    """
    print("Deleting tags...")

    lines_to_write = []

    with open("./data/atc_codes.csv", "r") as file:
        lines = file.readlines()
        for line in lines:
            if "[DG:" in line:
                line_without_tag = line.split(" ")[:-1]
                lines_to_write.append(" ".join(line_without_tag) + "\n")
            else:
                lines_to_write.append(line)

    with open("./data/atc_codes.csv", "w") as file:
        for line in lines_to_write:
            file.write(line)
    print("Done !")

def load(spark):
    """
    Load atc_codes.csv into a PySpark data frame
    """
    parse_atc()
    delete_tags()
    atc = spark.read.csv("./data/atc_codes.csv", header=True)
    atc.cache()
    return atc

def search(atc_codes_list, atc_df):
    """
    Search for medicine names corresponding to the ATC codes in `atc_codes_list`
    """
    searched_medicines = atc_df.filter(col("ATCCode").isin(atc_codes_list)).select("Description").collect()
    medicines = [medicine.Description for medicine in searched_medicines]

    return medicines


