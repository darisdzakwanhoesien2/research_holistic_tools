import pandas as pd

df = pd.read_csv("data/registry/master_registry.csv")

md = "# 📚 Master Literature Registry\n\n"

for doi, g in df.groupby("DOI"):
    md += f"## DOI: `{doi}`\n\n"

    row = g.iloc[0]
    md += f"""**Title:** {row.get('bib_title') or row.get('Title')}

**Authors:** {row.get('bib_authors') or row.get('Authors')}

**Journal:** {row.get('bib_journal') or row.get('Journal')}

**Year:** {row.get('bib_year') or row.get('Year')}

### Metrics
"""

    for _, r in g.iterrows():
        md += f"- Citations: {r.get('Cited By')} (from `{r.get('source_csv')}`)\n"

    md += "\n---\n\n"

with open("exports/markdown/master_registry.md", "w") as f:
    f.write(md)
