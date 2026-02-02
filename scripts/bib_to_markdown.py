import re

with open("data/references.bib") as f:
    content = f.read()

entries = re.findall(r"@article{([^}]+)}", content, re.DOTALL)

md = "# 📑 Bibliography\n\n"

for entry in entries:
    fields = dict(re.findall(r"(\w+)\s*=\s*[{](.*?)[}]", entry))
    md += f"""## {fields.get('title','')}

- **Authors**: {fields.get('author','')}
- **Journal**: {fields.get('journal','')}
- **Year**: {fields.get('year','')}
- **DOI**: `{fields.get('doi','')}`
- **Litmaps ID**: {fields.get('litmapsId','')}

---

"""

with open("exports/references.md", "w") as f:
    f.write(md)
