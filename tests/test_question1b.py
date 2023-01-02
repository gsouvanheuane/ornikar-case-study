import pytest
from src import generate_agg_dept
from google.cloud import bigquery
@pytest.mark.parametrize(
    "mock_partnership_type, mock_begin_date, mock_end_date",
    [
        (["EURL"],"2019-01-01", "2022-01-01"),
        (['SASU', 'ME', 'SARL', 'SAS', 'EI'], "2019-02-15", "2022-05-21"),
        (['unknown_partnership'], "2019-02-15", "2022-05-21"),
        ([], "2019-02-15", "2022-05-21"),
        pytest.param(
            ["EURL"],"10-10-20", "10-10-22",
            marks=pytest.mark.xfail(strict=True,
                                    reason='Expected to fail because date is in wrong format: "DD-MM-YY"'),
        ),
        pytest.param(
            ["EURL"],"10-10-2020", "10-10-2022",
            marks=pytest.mark.xfail(strict=True,
                                    reason='Expected to fail because date is in wrong format: "DD-MM-YYYY"'),
        ),
        pytest.param(
            ["EURL"],"20-10-10", "22-10-10",
            marks=pytest.mark.xfail(strict=True,
                                    reason='Expected to fail because date is in wrong format: "YY-MM-DD"'),
        ),
        pytest.param(
            ["EURL"],"10/10/2020", "10/10/2022",
            marks=pytest.mark.xfail(strict=True,
                                    reason='Expected to fail because date is in wrong format: "DD/MM/YYYY"'),
        ),
        pytest.param(
            ["EURL"],"10-2020", "10-2022",
            marks=pytest.mark.xfail(strict=True,
                                    reason='Expected to fail because date is in wrong format: "MM-YYYY"'),
        ),
        pytest.param(
            ["EURL"],"2019", "2022",
            marks=pytest.mark.xfail(strict=True,
                                    reason='Expected to fail because date is in wrong format: "YYYY"'),
        ),
    ],
)

def test__generate_agg_dept_valid_param(mock_partnership_type, mock_begin_date, mock_end_date):
    try:
        generate_agg_dept(
            partnership_type= mock_partnership_type,
            begin_date = mock_begin_date,
            end_date = mock_end_date
        )
        validated = True
    except:
        validated = False
    assert validated

