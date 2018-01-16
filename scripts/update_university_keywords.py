import click
import pandas as pd
from datausa.attrs.models import University
from datausa.database import db


@click.command()
@click.option('--sheet_url', prompt='Spreadsheet URL',
              help='The spreadsheet containing the university abbreviation mappings.')
def update_keywords(sheet_url):
    abbr_df = pd.read_csv(sheet_url)
    univs_by_id = {u.id: u for u in University.query}
    for univ_id, name, abbrev in abbr_df.values:
        univ_obj = univs_by_id[univ_id]
        abbrevs = abbrev.split(",")
        if univ_obj.keywords and set(abbrevs) == set(univ_obj.keywords):
            # no update required!
            pass
        else:
            univ_obj.keywords = abbrevs
            db.session.add(univ_obj)
    db.session.commit()


if __name__ == '__main__':
    update_keywords()
