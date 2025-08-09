from pydantic import BaseModel, Field
from typing import List


class Tabela(BaseModel):
    tabela: str = Field(
        description="Valores do extrato em Markdown demonstrando as colunas e os valores de cada célula. **Apenas a tabela**"
    )
