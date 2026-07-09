from AnnotatorCore import setoncokbapitoken, validate_oncokb_token
from AnnotatorCore import processalterationevents, QueryType, MutationStatus

import os
TOKEN = os.environ["ONCOKB_TOKEN"]
INPUT_FILE = "exonic_maf.txt"        
OUTPUT_FILE = "exonic_maf_annotated.txt"

setoncokbapitoken(TOKEN)
validate_oncokb_token()
print("Token set and validated.")

processalterationevents(
    INPUT_FILE, OUTPUT_FILE, "", "", {}, False,
    QueryType.GENOMIC_CHANGE, None, False,
    mutation_status=MutationStatus.SOMATIC,
)
print("done")