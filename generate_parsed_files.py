import keg_parser
import subprocess

if __name__ == "__main__":
    print("Generate atc_codes.csv...")
    keg_parser.parse_atc()
    keg_parser.delete_tags()
    print("Done !")

    print("Generate parsed_stitch.tsv...")
    subprocess.run(["awk", "-f", "./stitch_parser.awk", "./data/chemical.sources.v5.0.tsv"])
    print("Done !")

