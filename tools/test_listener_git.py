"""One local check that a timed fetch cannot interrupt a rebase."""
from unittest.mock import call, patch

import listener


def test_pull_rebase() -> None:
    with patch.object(listener, "branch", return_value="main"), patch.object(listener, "git", side_effect=[(0, "fetched"), (0, "rebased")]) as git:
        assert listener.pull_rebase() == (0, "fetchedrebased")
        assert git.call_args_list == [
            call(*listener.NET, "fetch", "origin", "main", timeout=listener.NET_TIMEOUT),
            call("rebase", "--autostash", "FETCH_HEAD", timeout=None),
        ]

    with patch.object(listener, "branch", return_value="main"), patch.object(listener, "git", side_effect=[(124, "timed out")]) as git:
        assert listener.pull_rebase() == (124, "timed out")
        assert git.call_count == 1

    with patch.object(listener, "branch", return_value="main"), patch.object(listener, "git", side_effect=[(0, ""), (1, "conflict"), (0, "")]) as git:
        assert listener.pull_rebase() == (1, "conflict")
        assert git.call_args_list[-1] == call("rebase", "--abort", timeout=None)


if __name__ == "__main__":
    test_pull_rebase()
