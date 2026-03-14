# Plano de Implementacao: Skill Dra. Cynthia — Analise Criminal

## Fase 1: Criar SKILL.md da nova skill

- [x] Criar `skills/dra-cynthia-analise-criminal/SKILL.md` com:
  - [x] Frontmatter YAML (name, description com triggers especificos)
  - [x] Persona Dra. Cynthia e introducao
  - [x] Secao "Ferramentas Disponiveis" (MCP TecJustica + calculadora + DOCX + relatorio-audiencias)
  - [x] Secao "Principio de Economia"
  - [x] Workflow completo (Etapas 0-6)
  - [x] Estrutura do relatorio (4 secoes fixas + 4 condicionais)
  - [x] Tratamento de processo em fase inadequada
  - [x] Formatacao (fls., contradicoes em negrito, lacunas, checklist)
  - [x] Secao DOCX detalhada
  - [x] Regras de Ouro (12 regras)

### Detalhes Tecnicos

Seguir exatamente o design spec em `docs/superpowers/specs/2026-03-13-dra-cynthia-analise-criminal-design.md`. O SKILL.md deve seguir o padrao das skills existentes, com atencao a:
- Triggers especificos para evitar conflito com analise-processo-penal
- calculadora() incluida, buscar_precedentes() excluida (com nota explicativa)
- grep_movimentacoes com regex focado (nao ".*")
- Tratamento de fase inadequada (inquerito, sem denuncia)
- Criterio explicito para delegacao a relatorio-audiencias (3+ audiencias)
- Sem secao de visuais (output textual/DOCX)

## Fase 2: Integrar com skill penal existente

- [x] Adicionar secao "Skill Dra. Cynthia" em `skills/analise-processo-penal/SKILL.md`

### Detalhes Tecnicos

Adicionar a seguinte secao antes de "Regras de Ouro":

```markdown
### Skill Dra. Cynthia — Relatorio Criminal para Magistrado (instalada por default)
Para relatorio estruturado de processo criminal com anotacoes por folhas, preparacao para audiencia de instrucao, e organizacao de provas e depoimentos, invoque a skill `dra-cynthia-analise-criminal`.
```

## Fase 3: Atualizar README

- [x] Adicionar secao da Dra. Cynthia no `README.md`
- [x] Adicionar exemplos de uso

### Detalhes Tecnicos

Adicionar secao apos "Relatorio de Audiencias" com descricao da skill e exemplos de uso no bloco de exemplos.

## Fase 4: Validacao e commit

- [ ] Verificar consistencia do SKILL.md com skills existentes
- [ ] Verificar referencias cruzadas
- [ ] Commit final
