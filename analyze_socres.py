import pandas as pd
# 1. Load the annotated file
df = pd.read_csv("exonic_toolscores_oncokb_apicall.txt", sep="\t", low_memory=False)
print("Total rows:", len(df))

# 2. Keep only rows OncoKB actually annotated
df = df[df["ANNOTATED"] == True]
print("Annotated rows:", len(df))

# 3. Look at the label distribution
print("\nONCOGENIC distribution:")
print(df["ONCOGENIC"].value_counts(dropna=False))

# 4. Define usable labels
#    positives = Oncogenic / Likely Oncogenic ; negative = Likely Neutral only
positives = ["Oncogenic", "Likely Oncogenic"]
negatives = ["Likely Neutral"]
df_labeled = df[df["ONCOGENIC"].isin(positives + negatives)].copy()
df_labeled["label"] = df_labeled["ONCOGENIC"].isin(positives).astype(int)
print("\nUsable labeled rows:", len(df_labeled))
print(df_labeled["label"].value_counts())   # 1 = oncogenic, 0 = neutral

# 5. Check missingness in the 8 tool-score columns
tool_cols = ["VEST4_score","REVEL_score","MutPred_score","PrimateAI_score",
             "VARITY_R_score","VARITY_ER_score","ESM1b_score","EVE_score","AlphaMissense_score"]
for c in tool_cols:
    df_labeled[c] = pd.to_numeric(df_labeled[c], errors="coerce")   # "." -> NaN
print("\nMissing values per tool (within labeled set):")
print(df_labeled[tool_cols].isna().sum())