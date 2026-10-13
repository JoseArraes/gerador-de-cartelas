#!/usr/bin/env python3
"""
Gerador de Cartelas Numeradas — cria imagens com grades de números
(1 a 50, 51 a 100...) e, se você quiser, encaixa cada grade dentro de uma
arte pronta (um layout .png feito no Photoshop ou Canva).

Útil para bingos, sorteios, listas de chamada numeradas e campanhas.

Exemplos:
  # 4500 números, 50 por cartela, só as grades
  python gerar_cartelas.py --total 4500 --por-cartela 50

  # encaixando cada grade na sua arte
  python gerar_cartelas.py --total 4500 --por-cartela 50 --layout arte.png --posicao 61 864 --tamanho 960 520
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def carregar_fonte(tamanho):
    for nome in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def criar_grade(inicio, fim, largura, altura, colunas, linhas, fonte):
    """Desenha uma grade de números com fundo transparente."""
    img = Image.new("RGBA", (largura, altura), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    cel_l, cel_a = largura // colunas, altura // linhas

    numero = inicio
    for linha in range(linhas):
        for coluna in range(colunas):
            if numero > fim:
                return img
            x, y = coluna * cel_l, linha * cel_a
            draw.rectangle([x, y, x + cel_l - 1, y + cel_a - 1], fill="white", outline="black", width=2)
            texto = str(numero)
            caixa = draw.textbbox((0, 0), texto, font=fonte)
            tl, ta = caixa[2] - caixa[0], caixa[3] - caixa[1]
            draw.text((x + (cel_l - tl) // 2 - caixa[0], y + (cel_a - ta) // 2 - caixa[1]),
                      texto, fill="black", font=fonte)
            numero += 1
    return img


def main():
    p = argparse.ArgumentParser(description="Gera cartelas numeradas em PNG.",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--total", type=int, required=True, help="último número (ex.: 4500)")
    p.add_argument("--por-cartela", type=int, default=50, help="números em cada cartela (padrão: 50)")
    p.add_argument("--colunas", type=int, default=5, help="colunas da grade (padrão: 5)")
    p.add_argument("--tamanho", type=int, nargs=2, default=[960, 520], metavar=("LARG", "ALT"),
                   help="tamanho da grade em pixels (padrão: 960 520)")
    p.add_argument("--layout", help="arte .png onde a grade será encaixada (opcional)")
    p.add_argument("--posicao", type=int, nargs=2, default=[0, 0], metavar=("X", "Y"),
                   help="canto superior esquerdo da grade dentro da arte")
    p.add_argument("--fonte", type=int, default=40, help="tamanho da fonte dos números (padrão: 40)")
    p.add_argument("--pasta", default="saida", help="pasta de saída (padrão: saida)")
    a = p.parse_args()

    if a.total < 1 or a.por_cartela < 1 or a.colunas < 1:
        sys.exit("[ERRO] total, por-cartela e colunas precisam ser maiores que zero.")

    linhas = -(-a.por_cartela // a.colunas)  # arredonda para cima
    largura, altura = a.tamanho
    fonte = carregar_fonte(a.fonte)

    layout = None
    if a.layout:
        if not os.path.isfile(a.layout):
            sys.exit(f"[ERRO] Arte não encontrada: {a.layout}")
        layout = Image.open(a.layout).convert("RGBA")

    os.makedirs(a.pasta, exist_ok=True)
    cartela = 0
    for inicio in range(1, a.total + 1, a.por_cartela):
        cartela += 1
        fim = min(inicio + a.por_cartela - 1, a.total)
        grade = criar_grade(inicio, fim, largura, altura, a.colunas, linhas, fonte)
        if layout is not None:
            final = layout.copy()
            final.paste(grade, tuple(a.posicao), grade)
        else:
            final = Image.new("RGBA", grade.size, "white")
            final.paste(grade, (0, 0), grade)
        final.convert("RGB").save(os.path.join(a.pasta, f"cartela_{cartela:03d}.png"))

    print(f"Pronto! {cartela} cartela(s) em '{a.pasta}'.")


if __name__ == "__main__":
    main()
