# NanotechSoft-Cifras v7

`./gerar.sh` lê todos os repertórios. Se uma música estiver sem URL, tenta localizar automaticamente uma página pública no CifraNET por música + artista, valida o resultado e só então baixa. Se não encontrar, mantém PENDENTE para edição manual.

Formato: `Numero|Musica|Artista|Tom|URL|Semitons|Observacao`

Metadados: `# NOME: Rock` e `# APELIDO: Banda X`.

No terminal aparecem `BUSCA`, `OK` e `PENDENTE`. O processo não contorna bloqueios ou anti-bot.
