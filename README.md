# GMD

GMD Project (2A): Development of a biomedical data integration system.
Contributors:
- ALONZO Léo
- DÉNÈS François
- RIOUX Lucas

## Requirements

- flask last version
- pyspark 3.3.2 with hadoop 2.7+
- python 3.10 + (not tested with earlier version)

## Launch the app

NOTE : the data is currently unavailable.
Put all the data files in a `data` repository, at the root of this git repository.

Run the file in web/app.py
Then go to the url : 127.0.0.1:5000

## Generate the data

1. We added headers to each meddra tsv file. Beware of the tabulations : each column is separeted by a tab '\t' character.
The headers :
- meddra : 
```
umls_concept_id	kind_of_term	meddra_id	side_effect
```
- meddra_all_indications :
```
stitch_flat_id	umls_concept_id_label	method_of_detection	concept_name	meddra_concept_type	umls_concept_id_meddra_team	meddra_concept_name
```

- meddra_all_se :
```
stitch_flat_id	stitch_stereo_id	umls_concept_id_label	meddra_concept_type	umls_concept_id_meddra_team	side_effect
```

- meddra_freq (unused) :
```
stitch_flat_id	stitch_stereo_id	umls_concept_id_label	is_placebo	frequency	lower_bound	upper_bound	meddra_concept_type	umls_concept_id_meddra_team	side_effect
```

If you haven't the headers, please add them manually.

2. We parsed `chemical.sources.v5.0.tsv` to only select the entries with an ATC code. This task is performed by the awk script `stitch_parser.awk`. The file name is `parsed_stitch.tsv`.

3. We parsed `br08303.keg` to select the ATC codes and their respective medicines. This task is performed by the functions `parse_atc()` and `delete_tags()` in the python file `keg_parser.py`. The file name is `atc_codes.csv`.

To generate the files `parsed_stitch.tsv` and `atc_codes.csv`, execute the python file `generate_parsed_files.py`.

## Usage:

Use the search query at the top left of the app to search a term. you can acces the results at the top right.
In the search query you can use:
- Keyword "ET" or "OU" to search seperate term and merge with intersection for "ET" and union for "OU"
- You can use "\*" for any character you want to match (equivalent to a .* in regex)
