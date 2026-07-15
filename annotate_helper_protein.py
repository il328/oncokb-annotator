from AnnotatorCore import setoncokbapitoken, validate_oncokb_token
from AnnotatorCore import processalterationevents, QueryType, MutationStatus

import os
TOKEN = "d6ed9c4e-e823-43eb-9705-b7c88c7e0eb1"
INPUT_FILE = "hersh_exome_biallelic_annovar_annotated.hg38_multianno.requested_predictor_scores.tsv"        
OUTPUT_FILE = "exonic_toolscores_oncokb_apicall.txt"


setoncokbapitoken(TOKEN)
validate_oncokb_token()
print("Token set and validated.")

processalterationevents(
    INPUT_FILE, OUTPUT_FILE, "", "", {}, False,
    QueryType.HGVSP_SHORT, None, False,
    mutation_status=MutationStatus.SOMATIC,
)

print("Done")
