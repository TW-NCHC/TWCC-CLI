from twcc import Session2
import pytest
from click.testing import CliRunner

@pytest.mark.first
def test_init_twcc_session():
    import shutil
    import os
    shutil.rmtree( os.path.dirname(Session2._getSessionFile()) )
    assert Session2._getApiKey() == os.environ.get('TWCC_API_KEY')

    mySession = Session2()
    assert mySession.getApiKey() == Session2._getApiKey()

from examples.twccli import cli

def test_list_cntr():
    runner = CliRunner()
    result = runner.invoke(cli, ['ls', '-c'])
    assert result.exit_code == 0


def test_list_cos():
    runner = CliRunner()
    result = runner.invoke(cli, ['ls', '-o'])
    assert result.exit_code == 0

