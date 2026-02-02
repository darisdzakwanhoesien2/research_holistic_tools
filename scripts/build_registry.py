import pandas as pd
import glob
import re

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def normalize_doi(doi):
    if pd.isna(doi):
        return None
    doi = str(doi).lower().strip()
    doi = doi.replace("https://doi.org/", "")
    return doi


# --------------------------------------------------
# Load ALL CSVs
# --------------------------------------------------
csv_files = glob.glob("data/csv/*.csv")

csv_frames = []
for f in csv_files:
    df = pd.read_csv(f)
    df["source_csv"] = f
    df["DOI"] = df["DOI"].apply(normalize_doi)
    csv_frames.append(df)

csv_df = pd.concat(csv_frames, ignore_index=True)

# --------------------------------------------------
# Load ALL BibTeX files
# --------------------------------------------------
bib_files = glob.glob("data/bib/*.bib")

bib_records = []

for bf in bib_files:
    with open(bf) as f:
        text = f.read()

    entries = re.findall(r"@article{([^}]+)}", text, re.DOTALL)

    for entry in entries:
        fields = dict(re.findall(r"(\w+)\s*=\s*[{](.*?)[}]", entry))
        doi = normalize_doi(fields.get("doi"))
        if doi:
            bib_records.append({
                "DOI": doi,
                "bib_title": fields.get("title"),
                "bib_authors": fields.get("author"),
                "bib_journal": fields.get("journal"),
                "bib_year": fields.get("year"),
                "source_bib": bf
            })

bib_df = pd.DataFrame(bib_records)

# --------------------------------------------------
# Merge (DOI = key)
# --------------------------------------------------
registry = pd.merge(
    csv_df,
    bib_df,
    on="DOI",
    how="outer",
    indicator=True
)

# --------------------------------------------------
# Save registry
# --------------------------------------------------
registry.to_csv("data/registry/master_registry.csv", index=False)

print("✅ Master registry built:", len(registry), "records")
