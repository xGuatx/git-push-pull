#!/usr/bin/env python3
"""
Pipeline Git complete
"""

import os
import subprocess


def normalize_repo_url(url):
    """Nettoie l'URL pour GitHub en supprimant https:// ou http://"""
    url = url.strip().replace("https://", "").replace("http://", "")
    return url


def need_pull():
    """Detecte si la branche locale a du retard"""
    subprocess.run(["git", "fetch"], capture_output=True)
    status = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
    return "Your branch is behind" in status.stdout


def safe_run(cmd, silent=False, allow_fail=False):
    """Wrapper propre pour executer une commande Git"""
    try:
        if silent:
            result = subprocess.run(cmd, capture_output=True, text=True, check=not allow_fail)
        else:
            result = subprocess.run(cmd, text=True, check=not allow_fail)
        return result
    except subprocess.CalledProcessError as e:
        if allow_fail:
            return e
        raise e


def pipeline_git_complete(nom_projet, url_repository, nom_utilisateur, token_acces=None, mode_sync="auto"):

    try:
        print("=== Pipeline Git Complete ===")

        # 0. Verification dossier
        if os.path.isdir(nom_projet):
            os.chdir(nom_projet)
            print(f"[INFO] Dossier detecte  {os.getcwd()}")
        else:
            print(f"[ERREUR] Le dossier '{nom_projet}' est introuvable.")
            return False

        # 1. Config user.name uniquement
        print("1. Configuration Git...")
        safe_run(["git", "config", "--global", "user.name", nom_utilisateur])
        print(f"[OK] user.name defini  {nom_utilisateur}")

        # 2. Init repo
        print("2. Initialisation du repository local...")
        if not os.path.exists(".git"):
            safe_run(["git", "init"])
            print("[OK] Repository initialise")
        else:
            print("[INFO] Repository deja initialise")

        # 3. .gitignore
        print("3. Verification du .gitignore...")
        if not os.path.exists(".gitignore"):
            with open(".gitignore", "w") as f:
                f.write("__pycache__/\n*.pyc\n*.log\nenv/\n.venv/\n")
            print("[OK] .gitignore cree")
        else:
            print("[INFO] .gitignore deja present")

        # 4. Add
        print("4. Ajout des fichiers...")
        safe_run(["git", "add", "."])
        print("[OK] Fichiers ajoutes")

        # 5. Commit si necessaire
        print("5. Commit...")
        status = safe_run(["git", "status", "--porcelain"], silent=True)
        if status.stdout.strip():
            safe_run(["git", "commit", "-m", "Initial commit - Configuration du projet"])
            print("[OK] Commit effectue")
        else:
            print("[INFO] Aucun changement a committer")

        # 6. Remote
        print("6. Configuration du remote...")

        url_repository = normalize_repo_url(url_repository)

        remote = safe_run(["git", "remote", "get-url", "origin"], allow_fail=True)

        if isinstance(remote, subprocess.CalledProcessError):
            # Nouveau remote
            if token_acces:
                url_complete = f"https://{nom_utilisateur}:{token_acces}@{url_repository}"
            else:
                url_complete = f"https://{url_repository}"

            safe_run(["git", "remote", "add", "origin", url_complete])
            print("[OK] Remote ajoute")
        else:
            print("[INFO] Remote deja present  mise a jour")
            if token_acces:
                url_complete = f"https://{nom_utilisateur}:{token_acces}@{url_repository}"
            else:
                url_complete = f"https://{url_repository}"

            safe_run(["git", "remote", "set-url", "origin", url_complete])
            print("[OK] Remote mis a jour")

        # 7. Ensure main branch
        print("7. Configuration de la branche main...")
        safe_run(["git", "branch", "-M", "main"], allow_fail=True)
        print("[OK] Branche definie sur main")

        # 8. Synchronisation
        print("8. Synchronisation...")

        if mode_sync == "auto":
            print("[AUTO] Analyse du repository...")
            if need_pull():
                mode_sync = "pull"
                print("[INFO] Le repo est en retard  pull")
            else:
                mode_sync = "push"
                print("[INFO] Aucun commit distant plus recent  push")

        if mode_sync == "pull":
            print("[PULL] Recuperation du code distant...")

            # premiere tentative simple
            result = subprocess.run(
                ["git", "pull", "origin", "main", "--allow-unrelated-histories"],
                text=True,
                capture_output=True
            )

            if result.returncode != 0:
                print("[WARN] Pull impossible  resolution automatique des branches divergentes")
                print(result.stderr.strip())

                # 2eme tentative : rebase propre
                result2 = subprocess.run(
                    ["git", "pull", "--rebase", "origin", "main"],
                    text=True
                )

                if result2.returncode != 0:
                    print("[ERREUR] La resolution automatique a echoue.")
                    return False

            print("[OK] Pull effectue")

        elif mode_sync == "force":
            print("[FORCE PUSH]  Ecrasement du contenu distant...")
            safe_run(["git", "push", "origin", "main", "--force"])
            print("[OK] Force push termine")

        elif mode_sync == "push":
            print("[PUSH] Envoi du code...")
            result = safe_run(["git", "push", "-u", "origin", "main"], allow_fail=True)

            if isinstance(result, subprocess.CalledProcessError):
                print("[ERREUR] Push impossible  un commit distant existe deja.")
                print(" Solutions : pull / force / suppression du repo GitHub.")
                return False

            print("[OK] Push effectue")

        print("\n=== Pipeline Terminee ===")
        return True

    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Commande Git echouee : {e}")
        print(" Vous devrez peut-etre corriger manuellement.")
        return False

    except Exception as e:
        print(f"[ERREUR] Exception inattendue : {e}")
        return False


if __name__ == "__main__":
    print("=== Test de la Pipeline Git ===")
    print("Configuration Git automatisee pour un nouveau projet.\n")

    nom_projet = input("Nom du projet : ")
    url_repo = input("URL du repository (ex: https://github.com/user/repo) : ")
    nom_user = input("Nom d'utilisateur Git : ")
    token = input("Token (optionnel) : ").strip() or None
    mode = input("Mode (auto/push/pull/force) [auto] : ").strip() or "auto"

    print("\nDemarrage de la pipeline...\n")

    pipeline_git_complete(nom_projet, url_repo, nom_user, token_acces=token, mode_sync=mode)

