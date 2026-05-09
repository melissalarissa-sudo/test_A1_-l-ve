"""
Agent IA avec outils — powered by Claude Opus 4.7
Exemple d'un agent conversationnel capable d'utiliser des outils.
"""

import anthropic
import math
import json
from datetime import datetime
from anthropic import beta_tool

client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY depuis l'environnement


# ── Définition des outils ────────────────────────────────────────────────────

@beta_tool
def get_current_datetime() -> str:
    """Retourne la date et l'heure actuelles."""
    now = datetime.now()
    return now.strftime("Le %d/%m/%Y à %H:%M:%S")


@beta_tool
def calculate(expression: str) -> str:
    """Évalue une expression mathématique.

    Args:
        expression: Expression mathématique à calculer (ex: "2 + 2", "sqrt(16)", "3.14 * 5**2").
    """
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "pow": math.pow, "log": math.log,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
        return f"Résultat de `{expression}` = {result}"
    except Exception as exc:
        return f"Erreur de calcul : {exc}"


@beta_tool
def search_knowledge(query: str, topic: str = "général") -> str:
    """Recherche des informations sur un sujet.

    Args:
        query: La question ou le sujet à rechercher.
        topic: Domaine de recherche (ex: "science", "histoire", "technologie").
    """
    # Dans un vrai projet, on appellerait une API de recherche ici.
    # Ceci est une réponse simulée pour la démonstration.
    knowledge_base = {
        "python": "Python est un langage de programmation interprété, créé par Guido van Rossum en 1991.",
        "claude": "Claude est un assistant IA développé par Anthropic, conçu pour être utile, inoffensif et honnête.",
        "anthropic": "Anthropic est une entreprise spécialisée en sécurité de l'IA, fondée en 2021.",
        "ia": "L'intelligence artificielle est la simulation de processus d'intelligence humaine par des machines.",
    }
    query_lower = query.lower()
    for key, value in knowledge_base.items():
        if key in query_lower:
            return value
    return f"Aucun résultat trouvé pour '{query}' dans le domaine '{topic}'. (Connectez une vraie API de recherche ici.)"


# ── Boucle de conversation ────────────────────────────────────────────────────

def run_agent():
    """Lance l'agent en mode conversationnel."""
    print("=" * 60)
    print("  Agent IA — Claude Opus 4.7")
    print("  Outils disponibles : calcul, date/heure, recherche")
    print("  Tapez 'quitter' pour arrêter.")
    print("=" * 60)
    print()

    tools = [get_current_datetime, calculate, search_knowledge]
    conversation: list[dict] = []

    while True:
        try:
            user_input = input("Vous : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAu revoir !")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quitter", "exit", "quit"):
            print("Au revoir !")
            break

        conversation.append({"role": "user", "content": user_input})

        # Le tool runner gère automatiquement la boucle outil → résultat → Claude
        runner = client.beta.messages.tool_runner(
            model="claude-opus-4-7",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=(
                "Tu es un assistant IA francophone, utile et précis. "
                "Tu peux utiliser des outils pour répondre aux questions. "
                "Réponds toujours en français."
            ),
            tools=tools,
            messages=conversation,
        )

        # Collecte la réponse finale
        final_text = ""
        for message in runner:
            for block in message.content:
                if block.type == "text" and block.text:
                    final_text = block.text

        if final_text:
            print(f"\nAssistant : {final_text}\n")
            # Ajoute la réponse de l'assistant à l'historique
            conversation.append({"role": "assistant", "content": final_text})
        else:
            print("\nAssistant : (aucune réponse)\n")


if __name__ == "__main__":
    run_agent()
