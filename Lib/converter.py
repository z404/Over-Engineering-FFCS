import tabula

import pandas as pd

df = tabula.read_pdf("lol.pdf")
print(df)
