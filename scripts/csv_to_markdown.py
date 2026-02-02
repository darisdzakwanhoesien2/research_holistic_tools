import pandas as pd

df = pd.read_csv("data/papers.csv")

md = "# 📚 Literature Records\n\n"

for _, r in df.iterrows():
    md += f"""## {r['Title']}

- **DOI**: `{r['DOI']}`
- **Authors**: {r['Authors']}
- **Journal**: {r['Journal']}
- **Year**: {r['Year']}
- **Citations**: {r['Cited By']}
- **Litmaps ID**: {r['LitmapsId']}
- **Tags**: {r['Tags']}

---

"""

with open("exports/papers.md", "w") as f:
    f.write(md)
