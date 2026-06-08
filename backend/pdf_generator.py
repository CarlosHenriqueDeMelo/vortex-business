from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os

def gerar_pdf_venda(venda, itens, empresa, cliente=None):
    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    os.makedirs(downloads, exist_ok=True)
    nome_arquivo = os.path.join(downloads, f"venda_{venda['id']}.pdf")

    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4

    logo_path = empresa.get('foto_path')
    if logo_path:
        logo_path = os.path.normpath(logo_path)
    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, 50, altura - 85, width=70, height=70, preserveAspectRatio=True, mask='auto')
        c.setFont("Helvetica-Bold", 18)
        c.drawString(130, altura - 50, empresa['nome'])

    else:
        c.setFont("Helvetica-Bold", 22)
        c.drawString(50, altura - 50, empresa['nome'])


    c.setFont("Helvetica", 10)
    c.drawRightString(largura - 50, altura - 50, f"Venda #{venda['id']}")
    c.drawRightString(largura - 50, altura - 65, f"Data: {venda['data_venda']}")
    c.drawRightString(largura - 50, altura - 80, f"Pagamento: {venda['forma_pagamento']}")

    c.setStrokeColor(colors.HexColor('#534AB7'))
    c.setLineWidth(1.5)
    c.line(50, altura - 90, largura - 50, altura - 90)
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)

    y_cliente = altura - 110
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_cliente, "Cliente")
    c.setFont("Helvetica", 11)
    if cliente:
        c.drawString(50, y_cliente - 18, f"Nome: {cliente.get('nome', '—')}")
        c.drawString(50, y_cliente - 34, f"Cidade: {cliente.get('cidade', '—')}")
        c.drawString(300, y_cliente - 18, f"Telefone: {cliente.get('telefone', '—')}")
        c.drawString(300, y_cliente - 34, f"ID: #{cliente.get('id', '—')}")
    else:
        c.drawString(50, y_cliente - 18, "Cliente nao informado")

    c.line(50, y_cliente - 48, largura - 50, y_cliente - 48)

    y_header = y_cliente - 68
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor('#534AB7'))
    c.drawString(50, y_header, "Produto")
    c.drawString(310, y_header, "Qtd")
    c.drawString(375, y_header, "Preco unit.")
    c.drawString(470, y_header, "Subtotal")
    c.setFillColor(colors.black)

    c.line(50, y_header - 10, largura - 50, y_header - 10)

    c.setFont("Helvetica", 11)
    y = y_header - 28
    for item in itens:
        c.drawString(50, y, str(item.get('nome', '')))
        c.drawString(310, y, str(item['quantidade']))
        c.drawString(375, y, f"R$ {item['preco_unitario']:.2f}")
        c.drawString(470, y, f"R$ {item['subtotal']:.2f}")
        y -= 22

    c.line(50, y - 5, largura - 50, y - 5)

    if venda.get('desconto') and venda['desconto'] > 0:
        c.setFont("Helvetica", 11)
        c.drawString(375, y - 20, f"Desconto: {venda['desconto']}%")
        y -= 18

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor('#534AB7'))
    c.drawString(375, y - 22, "Total:")
    c.drawString(470, y - 22, f"R$ {venda['total']:.2f}")
    c.setFillColor(colors.black)

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(largura / 2, 30, "Gerado por Vortex Business")
    c.setFillColor(colors.black)

    c.save()
    return nome_arquivo
