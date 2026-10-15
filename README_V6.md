# NanotechSoft-Cifras v6

Agora `./gerar.sh` lê TODOS os arquivos `repertorios/*.txt`.

Formato recomendado:
`Numero|Musica|Artista|Tom|URL|Semitons|Observacao`

No início de cada arquivo:
`# NOME: Rock`
`# APELIDO: Banda X`

- Com URL: tenta baixar a cifra.
- Sem URL: entra como PENDENTE e pode ser preenchida em EDITAR.
- Uma música repetida em vários repertórios fica uma única vez na biblioteca.
- Cada repertório mantém sua própria ordem.
- `repertorios/rock.txt` já está incluído como exemplo/segundo repertório.

IMPORTANTE: repertórios criados apenas dentro do navegador ficam no armazenamento local. Para que `./gerar.sh` baixe suas fontes numa nova geração, mantenha também o respectivo TXT em `repertorios/`.
