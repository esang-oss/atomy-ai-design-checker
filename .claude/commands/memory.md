# /memory — memtemple vault command

Maps to `atomy-toolkit memtemple <sub>`. Use:

- `/memory save --plugin claude_code --source <jsonl>` — save a session to vault
- `/memory recall <query>` — BM25 search (add `--llm` for LM-as-searcher)
- `/memory list [--last N]` — recent N entries
- `/memory show <drawer_path>` — full drawer
- `/memory status` — vault stats

See: docs/specs/2026-05-20-memtemple-v1-design.md
