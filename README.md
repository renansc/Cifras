# NanotechSoft-Cifras

Aplicativo de repertórios e cifras com carrossel 3D, controle remoto pelo celular e apresentação em TV pela rede local.

## Executar

Na pasta do aplicativo, execute:

```bash
python3 servidor_tv.py --port 8000
```

Abra no navegador do celular `http://IP_DO_SERVIDOR:8000/controle` e na TV `http://IP_DO_SERVIDOR:8000/tv`.

Para utilização offline em uma tela, abra `saida/NanotechSoft-Cifras.html`.

## Publicação do código

Os arquivos do projeto devem ser enviados para a raiz deste repositório, incluindo `servidor_tv.py`, `tv.html`, `gerar.sh`, `app/`, `saida/`, `assets/`, `repertorios/` e demais arquivos necessários. Evite publicar backups com informações pessoais ou chaves de acesso.
