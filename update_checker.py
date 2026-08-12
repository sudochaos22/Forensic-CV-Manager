from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class UpdateResult:
    current_version: str
    latest_version: str
    release_url: str
    update_available: bool
    message: str = ""


def _version_tuple(value: str) -> tuple[int, ...]:
    value = value.strip().lower().lstrip("v")
    parts = []
    for token in value.split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)


def _validate_repository(repository: str) -> str:
    repository = repository.strip().strip("/")
    if not repository or repository.upper() == "OWNER/REPOSITORY":
        raise RuntimeError("The GitHub repository has not been configured in app_config.py.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise RuntimeError(
            "The GitHub repository must use the format owner/repository, for example: "
            "my-account/forensic-cv-manager."
        )
    return repository


def _request_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Forensic-CV-Manager",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def check_github_release(repository: str, current_version: str, timeout: int = 8) -> UpdateResult:
    repository = _validate_repository(repository)
    releases_url = f"https://api.github.com/repos/{repository}/releases/latest"

    try:
        payload = _request_json(releases_url, timeout)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            # GitHub returns 404 both when a repository is unavailable and when a
            # valid repository has no published Releases. Check the repository itself
            # so the user receives a useful explanation instead of a raw HTTP error.
            try:
                repo_payload = _request_json(f"https://api.github.com/repos/{repository}", timeout)
            except urllib.error.HTTPError as repo_exc:
                if repo_exc.code == 404:
                    raise RuntimeError(
                        f"The GitHub repository '{repository}' was not found. Verify the "
                        "owner/repository value and make sure the repository is public."
                    ) from repo_exc
                raise RuntimeError(f"GitHub returned HTTP {repo_exc.code} while checking the repository.") from repo_exc
            except urllib.error.URLError as repo_exc:
                raise RuntimeError(f"Could not reach GitHub: {repo_exc.reason}") from repo_exc

            repo_url = str(repo_payload.get("html_url") or f"https://github.com/{repository}")
            return UpdateResult(
                current_version=current_version,
                latest_version=current_version,
                release_url=repo_url,
                update_available=False,
                message=(
                    f"The repository '{repository}' is available, but it does not have a "
                    "published GitHub Release yet. Publish a Release with a version tag such "
                    f"as v{current_version} to enable update checking."
                ),
            )
        if exc.code == 403:
            raise RuntimeError(
                "GitHub temporarily refused the update request. Try again later; this can occur "
                "when the anonymous API rate limit has been reached."
            ) from exc
        raise RuntimeError(f"GitHub returned HTTP {exc.code} while checking for updates.") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach GitHub: {exc.reason}") from exc

    latest = str(payload.get("tag_name") or current_version)
    release_url = str(payload.get("html_url") or "")
    return UpdateResult(
        current_version=current_version,
        latest_version=latest,
        release_url=release_url,
        update_available=_version_tuple(latest) > _version_tuple(current_version),
        message="",
    )
