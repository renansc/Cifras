# NanotechSoft-Cifras v8.1

Ao executar `./gerar.sh`, o sistema verifica antes de gerar:

- `python3`
- `bs4` / BeautifulSoup (`python3-bs4`)
- `reportlab` (`python3-reportlab`)

Se algo estiver ausente, mostra exatamente o módulo faltante e tenta instalar automaticamente via APT. Em Linux sem pacote APT utilizável, tenta criar `.venv` e instalar o módulo via pip. Quando `sudo` for necessário, o terminal poderá pedir a senha do usuário.

Depois gera normalmente:

- `saida/NanotechSoft-Cifras.html`
- `saida/pdf/`

Uso:

```bash
./gerar.sh
```
