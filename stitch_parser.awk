#!/usr/bin/awk -f

BEGIN {
    print "[awk] Parsing chemical.sources.v5.0.tsv..."
    FS="\t"
    system("rm ./data/parsed_stitch.tsv")
    system("touch ./data/parsed_stitch.tsv")
    print "CIDm\tCIDs\tDatabase\tATCCode" >> "./data/parsed_stitch.tsv"
}

NR <= 9 {
    next
}

{
    if ($3 == "ATC") {
        nb_atc_codes += 1
        print $0 >> "./data/parsed_stitch.tsv"
    }
}

END {
    print nb_atc_codes
    print "[awk] Done !"
}


