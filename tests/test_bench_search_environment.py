import pytest
from scripts.bench_run import benchmark_environment


def test_default_benchmark_removes_all_search_credentials_and_selectors():
    env={'BRAVE_SEARCH_API_KEY':'fixture','SIGNALPOST_SEARCH_PROVIDER':'brave','OTHER_API_KEY':'fixture',
         'NAV_API_TOKEN':'fixture','SIGNALPOST_LLM_PROVIDER':'fixture','PATH':'test-path'}
    assert benchmark_environment(False,env)=={'PATH':'test-path'}


def test_explicit_search_keeps_only_brave_credentials_without_mutating_parent():
    env={'BRAVE_SEARCH_API_KEY':'fixture','SIGNALPOST_SEARCH_PROVIDER':'brave','OTHER_API_KEY':'fixture','PATH':'test-path'}
    result=benchmark_environment(True,env)
    assert result=={'BRAVE_SEARCH_API_KEY':'fixture','SIGNALPOST_SEARCH_PROVIDER':'brave','PATH':'test-path'}
    assert 'OTHER_API_KEY' in env


@pytest.mark.parametrize('env',[{}, {'BRAVE_SEARCH_API_KEY':'fixture'}, {'SIGNALPOST_SEARCH_PROVIDER':'brave'}])
def test_search_benchmark_requires_both_terminal_variables_without_echoing_values(env):
    with pytest.raises(ValueError) as exc:benchmark_environment(True,env)
    assert 'fixture' not in str(exc.value)
