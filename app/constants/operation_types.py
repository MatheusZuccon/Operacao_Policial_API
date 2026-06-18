from typing import Final

OSTENSIVE: Final[str] = "OSTENSIVE"
INVESTIGATIVE: Final[str] = "INVESTIGATIVE"
TACTICAL: Final[str] = "TACTICAL"

VALID_OPERATION_TYPES: Final[list[str]] = [OSTENSIVE, INVESTIGATIVE, TACTICAL]

OPERATION_TYPE_LABELS: Final[dict[str, str]] = {
    OSTENSIVE: "Operações Ostensivas e Preservação da Ordem",
    INVESTIGATIVE: "Operações de Polícia Judiciária e Investigativa",
    TACTICAL: "Operações de Forças Táticas e Especiais",
}
