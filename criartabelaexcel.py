import openpyxl



def criar_tabela_excel():
    lista_animes = openpyxl.Workbook()
    planilha = lista_animes.active
    planilha.title = "Animes"

    planilha.append(["Nome", "Gênero", "Episódios", "Nota"])
    planilha.append(["One Piece", "Aventura", 1000, 9.5])
    planilha.append(["Naruto", "Ação", 220, 8.5])

    lista_animes.save("animes.xlsx")


criar_tabela_excel()    