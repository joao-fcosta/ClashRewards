BASE_LEVELS = {
    "common": 1, "rare": 3, "epic": 6,
    "legendary": 9, "champion": 11
}

def calcular_novo_nivel_rei(cartas: list) -> int:
    niveis_absolutos = sorted(
        [BASE_LEVELS.get(c.get("rarity", "common"), 1) + c.get("level", 1) - 1 for c in cartas],
        reverse=True
    )
    
    def tem_cartas(qtd, lvl):
        return len(niveis_absolutos) >= qtd and niveis_absolutos[qtd - 1] >= lvl

    # Mapeamento do Rei
    if tem_cartas(14, 15): return 16
    if tem_cartas(13, 14): return 15
    if tem_cartas(12, 13): return 14
    if tem_cartas(11, 12): return 13
    if tem_cartas(11, 11): return 12
    if tem_cartas(10, 10): return 11
    if tem_cartas(10, 9):  return 10
    if tem_cartas(10, 8):  return 9
    if tem_cartas(10, 7):  return 8
    if tem_cartas(10, 6):  return 7
    if tem_cartas(10, 5):  return 6
    if tem_cartas(10, 4):  return 5
    if tem_cartas(10, 3):  return 4
    if tem_cartas(9, 2):   return 3
    if tem_cartas(9, 1):   return 2
    return 1

def calcular_nivel_rei_antigo(exp: int) -> int:
    niveis = {75: 16, 54: 15, 42: 14, 38: 13, 34: 12, 30: 11, 26: 10, 22: 9, 18: 8, 14: 7, 10: 6, 7: 5, 5: 4, 3: 3, 2: 2}
    for req_exp, nivel in niveis.items():
        if exp >= req_exp: return nivel
    return 1

def calcular_nivel_colecao(cartas_normais: list, tropas_torre: list) -> int:
    nivel_colecao = 0
    for carta in cartas_normais + tropas_torre:
        raridade = carta.get("rarity", "common")
        nivel_colecao += BASE_LEVELS.get(raridade, 1) + carta.get("level", 1) - 1
        if raridade == "champion": nivel_colecao += 5
        if carta.get("evolutionLevel", 0) > 0: nivel_colecao += 5
    return nivel_colecao

def calcular_recompensas(nivel: int) -> dict:
    if nivel >= 2001: return {"gems": "5.000", "baus": 3, "bandeiras": 6, "pele": 1}
    elif nivel >= 1801: return {"gems": "4.500", "baus": 3, "bandeiras": 6, "pele": 0}
    elif nivel >= 1601: return {"gems": "4.000", "baus": 2, "bandeiras": 5, "pele": 0}
    elif nivel >= 1401: return {"gems": "3.500", "baus": 2, "bandeiras": 4, "pele": 0}
    elif nivel >= 1201: return {"gems": "3.000", "baus": 1, "bandeiras": 3, "pele": 0}
    elif nivel >= 1001: return {"gems": "2.500", "baus": 1, "bandeiras": 2, "pele": 0}
    elif nivel >= 801: return {"gems": "2.000", "baus": 1, "bandeiras": 1, "pele": 0}
    elif nivel >= 601: return {"gems": "1.500", "baus": 0, "bandeiras": 0, "pele": 0}
    elif nivel >= 401: return {"gems": "1.000", "baus": 0, "bandeiras": 0, "pele": 0}
    elif nivel >= 201: return {"gems": "750", "baus": 0, "bandeiras": 0, "pele": 0}
    elif nivel >= 20: return {"gems": "500", "baus": 0, "bandeiras": 0, "pele": 0}
    return {"gems": "0", "baus": 0, "bandeiras": 0, "pele": 0}