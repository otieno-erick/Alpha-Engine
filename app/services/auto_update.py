from __future__ import annotations

import json
from urllib.request import Request, urlopen

from packaging.version import InvalidVersion, Version


class ReleaseUpdateChecker:
    def __init__(
        self,
        current_version: str,
        repository: str = "otieno-erick/Alpha-Engine",
        *,
        timeout: float = 10,
    ):
        self.current_version = Version(current_version)
        self.repository = repository
        self.timeout = timeout

    def check(self) -> dict[str, str | bool]:
        request = Request(
            f"https://api.github.com/repos/{self.repository}/releases/latest",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "Alpha-Engine",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            release = json.load(response)

        if not isinstance(release, dict):
            raise ValueError("GitHub latest-release response must be a JSON object")

        tag_name = release.get("tag_name")
        release_url = release.get("html_url")
        if not isinstance(tag_name, str) or not isinstance(release_url, str):
            raise ValueError("GitHub latest-release response is missing tag_name or html_url")

        latest_version_text = tag_name.removeprefix("v")
        try:
            latest_version = Version(latest_version_text)
        except InvalidVersion as exc:
            raise ValueError(f"GitHub release tag is not a valid version: {tag_name!r}") from exc

        return {
            "current_version": str(self.current_version),
            "latest_version": str(latest_version),
            "update_available": latest_version > self.current_version,
            "release_url": release_url,
        }
