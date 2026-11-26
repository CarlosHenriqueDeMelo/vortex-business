# Vortex Business

ERP para pequenos comércios, com aplicativo **desktop** e **mobile**, controle de vendas, financeiro e sincronização offline.

> Projeto pessoal em desenvolvimento ativo.

## Funcionalidades

- Cadastro de empresas, clientes, fornecedores e produtos
- Vendas, entradas de estoque e controle de fiado
- Financeiro com lançamentos e dashboard
- Geração de comprovante de venda em PDF
- Sincronização entre desktop e mobile (modo offline)

## Estrutura

| Pasta | Conteúdo | Tecnologias |
|---|---|---|
| `backend/` | API e regras de negócio | Python, Flask, SQLite, ReportLab |
| `frontend/` | Aplicativo desktop | Electron, HTML/CSS/JS |
| `mobile/` | Aplicativo mobile | React Native, Expo, TypeScript |

## Como rodar

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Desktop**
```bash
cd frontend
npm install
npm start
```

**Mobile**
```bash
cd mobile
npm install
npx expo start
```

## Segurança

- Credenciais e configurações ficam em `.env` (ignorado pelo Git).
- Bancos de dados locais (`*.db`) não são versionados.

## Roadmap

- [ ] Testes automatizados
- [ ] Hardening da API (validação de entrada, rate limiting)

## Licença

Veja `mobile/LICENSE`.

## Gerar instaladores

```bash
# Linux: ./scripts/build-backend.sh && cd frontend && npm install && npm run build:linux
# Windows: scripts\build-backend.bat  &&  cd frontend && npm install && npm run build:win
```

Celular (Android 7.0+): `cd mobile && npx expo prebuild --platform android && npx expo run:android --variant release`.
Na rede local o celular usa HTTP; no Windows, libere o Vortex no firewall quando o aviso aparecer.
